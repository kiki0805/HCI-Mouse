#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 TexCoord;
out vec3 Position;

uniform float xTrans, yTrans;

void main()
{
    gl_Position = vec4(aPos.x + xTrans, aPos.y + yTrans, aPos.z, 1.0);
    Position = aPos;
    TexCoord = vec2(aTexCoord.x, aTexCoord.y);
}