#version 330 core
out vec4 FragColor;
  
in vec2 TexCoord;
in vec3 Position;
uniform sampler2D texture0;

void main()
{
    FragColor = texture(texture0, TexCoord);
}