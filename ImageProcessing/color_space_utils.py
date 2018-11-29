def convert_XYZ2RGB(xyz_v):
    var_X = (float) (xyz_v.X / 100)
    var_Y = (float) (xyz_v.Y / 100)
    var_Z = (float) (xyz_v.Z / 100)

    var_R = var_X *  3.2406 + var_Y * -1.5372 + var_Z * -0.4986
    var_G = var_X * -0.9689 + var_Y *  1.8758 + var_Z *  0.0415
    var_B = var_X *  0.0557 + var_Y * -0.2040 + var_Z *  1.0570

    if var_R > 0.0031308:
        var_R = 1.055 * ( pow(var_R, ( 1 / 2.4 )) ) - 0.055
    else:
        var_R = 12.92 * var_R
    if var_G > 0.0031308:
        var_G = 1.055 * ( pow(var_G, ( 1 / 2.4 )) ) - 0.055
    else:
        var_G = 12.92 * var_G
    if var_B > 0.0031308:
        var_B = 1.055 * ( pow(var_B, ( 1 / 2.4 )) ) - 0.055
    else:
        var_B = 12.92 * var_B

    sR = var_R * 255
    sG = var_G * 255
    sB = var_B * 255
    return RGBValue(RGB=(sR, sG, sB))

def convert_RGB2XYZ(rgb_v):
    var_R = rgb_v.r
    var_G = rgb_v.g
    var_B = rgb_v.b

    if var_R > 0.04045:
        var_R = pow(( ( var_R + 0.055 ) / 1.055 ), 2.4)
    else:
        var_R = var_R / 12.92
    if var_G > 0.04045:
        var_G = pow(( ( var_G + 0.055 ) / 1.055 ), 2.4)
    else:
        var_G = var_G / 12.92
    if var_B > 0.04045:
        var_B = pow(( ( var_B + 0.055 ) / 1.055 ), 2.4)
    else:
        var_B = var_B / 12.92

    var_R = var_R * 100
    var_G = var_G * 100
    var_B = var_B * 100

    X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
    Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
    Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505
    return XYZValue(X=X, Y=Y, Z=Z)

def convert_XYZ2Lab(xyz_v):
    RefX = 95.047
    RefY = 100.000
    RefZ = 108.883
    var_X = (float) (xyz_v.X / RefX)
    var_Y = (float) (xyz_v.Y / RefY)
    var_Z = (float) (xyz_v.Z / RefZ)

    if var_X > 0.008856:
        var_X = pow(var_X, ( 1/3 ))
    else:
        var_X = ( 7.787 * var_X ) + ( 16 / 116 )
    if var_Y > 0.008856:
        var_Y = pow(var_Y, ( 1/3 ))
    else:
        var_Y = ( 7.787 * var_Y ) + ( 16 / 116 )
    if var_Z > 0.008856:
        var_Z = pow(var_Z, ( 1/3 ))
    else:
        var_Z = ( 7.787 * var_Z ) + ( 16 / 116 )

    L = ( 116 * var_Y ) - 16
    a = 500 * ( var_X - var_Y )
    b = 200 * ( var_Y - var_Z )
    return LABValue(L=L, a=a, b=b)

def convert_Lab2XYZ(Lab_v):
    RefX = 95.047
    RefY = 100.000
    RefZ = 108.883
    var_Y = ( Lab_v.L + 16 ) / 116
    var_X = Lab_v.a / 500 + var_Y
    var_Z = var_Y - Lab_v.b / 200

    # print(pow(var_Y, 3))
    if pow(var_Y, 3) > 0.008856:
        var_Y = pow(var_Y, 3)
    else:
        var_Y = ( var_Y - 16 / 116 ) / 7.787
    if pow(var_X, 3) > 0.008856:
        var_X = pow(var_X, 3)
    else:
        var_X = ( var_X - 16 / 116 ) / 7.787
    if pow(var_Z, 3)  > 0.008856:
        var_Z = pow(var_Z, 3)
    else:
        var_Z = ( var_Z - 16 / 116 ) / 7.787

    X = var_X * RefX
    Y = var_Y * RefY
    Z = var_Z * RefZ
    return XYZValue(X=X, Y=Y, Z=Z)

def convert_RGB2Lab(rgb_v):
    return convert_XYZ2Lab(convert_RGB2XYZ(rgb_v))

def convert_Lab2RGB(Lab_v):
    return convert_XYZ2RGB(convert_Lab2XYZ(Lab_v))

class RGBValue:
    def __init__(self, RGB=None, rgb=None):
        self.R = None
        self.G = None
        self.B = None
        self.r = None
        self.g = None
        self.b = None
        self.Lab = None
        self.XYZ = None
        if RGB is not None: 
            self.R = RGB[0]
            self.G = RGB[1]
            self.B = RGB[2]
            self.r = (float) (RGB[0] / 255.0)
            self.g = (float) (RGB[1] / 255.0)
            self.b = (float) (RGB[2] / 255.0)

        if rgb is not None:
            self.r = rgb[0]
            self.g = rgb[1]
            self.b = rgb[2]
            # self.R = (int) (rgb[0] * 255)
            # self.G = (int) (rgb[1] * 255)
            # self.B = (int) (rgb[2] * 255)
            self.R = (rgb[0] * 255)
            self.G = (rgb[1] * 255)
            self.B = (rgb[2] * 255)
    
    # def initialize_by_Lab(self, Lab_v):
    #     self.Lab = Lab_v
    #     self.initialize_by_XYZ(Lab_v.get_XYZ())

    # def initialize_by_XYZ(self, xyz_v):
    #     self.XYZ = xyz_v
    #     # convert xyz to rgb




    # def get_Lab(self):
    #     if self.Lab:
    #         return self.Lab
    
    # def get_XYZ(self):
    #     if self.XYZ:
    #         return self.XYZ
    #     # convert rgb to xyz



class LABValue:
    def __init__(self, L=None, a=None, b=None):
        self.L = L
        self.a = a
        self.b = b
        self.RGB = None
        self.XYZ = None

    # def initialize_by_RGB(self, rgb_v):
    #     self.RGB = rgb_v
    #     pass

    # def initialize_by_XYZ(self, xyz_v):
    #     self.XYZ = xyz_v

    # def get_RGB(self):
    #     if self.RGB:
    #         return self.RGB

    # def get_XYZ(self):
    #     if self.XYZ:
    #         return self.XYZ


class XYZValue:
    def __init__(self, X=None, Y=None, Z=None):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.RGB = None
        self.XYZ = None

    # def initialize_by_Lab(self, Lab_v):
    #     self.Lab = Lab_v
    
    # def initialize_by_RGB(self, rgb_v):
    #     self.RGB = rgb_v
    
    # def get_RGB(self):
    #     if self.RGB:
    #         return self.RGB
    
    # def get_Lab(self):
    #     if self.Lab:
    #         return self.Lab

