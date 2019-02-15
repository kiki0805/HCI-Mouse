#include "hcicontroller.h"
#include <cstdlib>

#include "multimouse.h"

using namespace npnx;

HCIInstance::HCIInstance(HCIController *parent, int mouseidx):
  mouseIdx(mouseidx),
  mParent(parent)
{
  wsprintf(senderPipePath, TEXT("%ls_%d"), HCICONTROLLER_PIPE_SENDER_PATH, mouseidx);
  printf("%ls\n", senderPipePath);
  wsprintf(receiverPipePath, TEXT("%ls_%d"), HCICONTROLLER_PIPE_RECEIVER_PATH, mouseidx);
  printf("%ls\n", receiverPipePath);
}

void HCIInstance::Start() {
  HANDLE hSenderPipe = CreateNamedPipe(senderPipePath, PIPE_ACCESS_DUPLEX,
                                 PIPE_TYPE_MESSAGE | PIPE_WAIT | PIPE_READMODE_MESSAGE,
                                 PIPE_UNLIMITED_INSTANCES,
                                 1,
                                 1, 1000, NULL);
  HANDLE hReceiverPipe = CreateNamedPipe(receiverPipePath, PIPE_ACCESS_DUPLEX,
                                        PIPE_TYPE_MESSAGE | PIPE_WAIT | PIPE_READMODE_MESSAGE,
                                        PIPE_UNLIMITED_INSTANCES,
                                        1,
                                        1, 1000, NULL);
  STARTUPINFO si;
  PROCESS_INFORMATION pi;
  memset(&si, 0, sizeof(STARTUPINFO));
  si.cb = sizeof(STARTUPINFO);
  memset(&pi, 0, sizeof(PROCESS_INFORMATION));
  WCHAR processCmd[8192];
  
  //if use python, add python at the beginning like this
  // wsprintf(processCmd, TEXT("python %ls/%ls %d %ls %ls"), TEXT(NPNX_PY_PATH), TEXT(NPNX_PY_EXECUTABLE), mouseIdx, senderPipePath, receiverPipePath);
  
  wsprintf(processCmd, TEXT("%ls/%ls %d %ls %ls"), TEXT(NPNX_PY_PATH), TEXT(NPNX_PY_EXECUTABLE), mouseIdx, senderPipePath, receiverPipePath);
  printf("processCmd %ls\n", processCmd);
  if (!CreateProcess(NULL,
                     processCmd,
                     NULL,
                     NULL,
                     FALSE,
                     0,
                     NULL,
                     NULL,
                     &si,
                     &pi)) {
    NPNX_ASSERT_LOG(false && "createPyProcessFailed", GetLastError());
  } else {
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
  }

  bool fConnected = ConnectNamedPipe(hSenderPipe, NULL) ? TRUE : (GetLastError() == ERROR_PIPE_CONNECTED);
  NPNX_ASSERT(fConnected && "sender");
  fConnected = ConnectNamedPipe(hReceiverPipe, NULL) ? TRUE : (GetLastError() == ERROR_PIPE_CONNECTED);
  NPNX_ASSERT(fConnected && "receiver");

  senderThread = std::thread([&, this](HANDLE hPipe){this->senderEntry(hPipe);}, hSenderPipe);
  receiverThread = std::thread([&, this](HANDLE hPipe){this->receiverEntry(hPipe);}, hReceiverPipe);
}

void HCIInstance::senderEntry(HANDLE hPipe) {
  while (true) {
    int nowState = messageType.load();
    switch (nowState) {
      case HCIMESSAGEINTYPE_POSITION:
        {
          unsigned char buf[255];
          mParent->core->ControlTransfer(mouseIdx, 0x40, 0x01, 0x0000, 0x010D, buf+1, 1, 1000);
          buf[0] = HCIMESSAGEINTYPE_POSITION;
          int cnt = mParent->core->ControlTransfer(0, 0xC0, 0x01, 0x0000, 0x0D, buf+1, 1, 1000);
          LIBUSB_CHECK_RET(hcisender_position_controlTrans, cnt);
          DWORD length = 0;
          NPNX_ASSERT_LOG(WriteFile(hPipe, buf, cnt+1, &length, NULL), GetLastError());
        }
        break;
      case HCIMESSAGEINTYPE_ANGLE_1:
      case HCIMESSAGEINTYPE_ANGLE_2:
        {
          unsigned char buf[4096];
          buf[0] = nowState;
          unsigned char tempbuf[255];
          mParent->core->ControlTransfer(mouseIdx, 0x40, 0x01, 0x0000, 0x010D, tempbuf, 1, 1000);
          for (int i = 0; i < 19*19; i++) {
            int cnt = mParent->core->ControlTransfer(0, 0xC0, 0x01, 0x0000, 0x0D, buf + 1 + i, 1, 1000);
            LIBUSB_CHECK_RET(hcisender_position_controlTrans, cnt);
          }
          DWORD length = 0;
          NPNX_ASSERT_LOG(WriteFile(hPipe, buf, 19 * 19 + 1, &length, NULL), GetLastError());
        }
        break;
      case HCIMESSAGEINTYPE_ANGLE_HALT:
        //reserved.
        break;
      case HCIMESSAGEINTYPE_EXIT:
        DisconnectNamedPipe(hPipe);
        CloseHandle(hPipe);
        return;
        break;
      default:
        NPNX_ASSERT(false && "HCIInstance send status error");
        break;
    }
    std::this_thread::yield();
  }
}

void HCIInstance::receiverEntry(HANDLE hPipe) {
  HCIMessageReport thisReport;
  memset(&thisReport, 0, sizeof(HCIMessageReport));
  while (true) {
    unsigned char buf[4096];
    DWORD length = 0;
    NPNX_ASSERT_LOG(ReadFile(hPipe, buf, 6, &length, NULL), GetLastError());
    thisReport.index = buf[0];
    thisReport.type = buf[1];
    switch (thisReport.type) {
      case HCIMESSAGEOUTTYPE_POSITION:
        thisReport.param2 = *(int16_t *)&(buf[4]);
        //no break
      case HCIMESSAGEOUTTYPE_ANGLE:
        thisReport.param1 = *(int16_t *)&(buf[2]);
        break;
      case HCIMESSAGEOUTTYPE_ANGLE_SIGNAL:
        break;
      default:
        LIBUSB_CHECK_RET_BUFFER_SIZE(hci_output_type_error, -1, buf, length);
        CloseHandle(hPipe);
        exit(-1);
        break;    
    }
    mParent->messageFifo.Push(thisReport);
    std::this_thread::yield();
  }
}

HCIController::HCIController(){
  instances.clear();
}

HCIController::~HCIController(){
  for(auto it: instances){
    delete it;
  }
  instances.clear();
}

void HCIController::Init(MultiMouseSystem *parent, int num_mouse) {
  core = &parent->core;
  mNumMouse = num_mouse;
  for (int i=0; i<num_mouse; i++) {
    instances.push_back(new HCIInstance(this, i));
  }
  mInitialized = true;
}

void HCIController::Start() {
  NPNX_ASSERT(mInitialized);
  for (auto it: instances) {
    it->Start();
  }
}