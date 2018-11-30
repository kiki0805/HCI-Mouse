cd $(dirname $0)

rm -rf build
mkdir -p build

cd build

cmake -G "Visual Studio 15 2017 Win64" ..
cmake --build . 
