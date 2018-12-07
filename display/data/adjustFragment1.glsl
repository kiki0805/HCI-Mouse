#version 330 core

out vec4 FragColor;

in vec2 TexCoord;
in vec3 Position;

uniform sampler2D texture0;
uniform sampler2D rawScreen;
uniform int letThrough;

void main()
{
  // Position ranges [-1.0, 1.0].
  vec4 rawColor = texture(rawScreen, (Position.xy + vec2(1.0, 1.0)) / vec2(2,2));
  vec4 newColor = texture(texture0, TexCoord);
  if (Position.y > -0.1) {
    newColor *= vec4(1.0, 0.0, 0.0, 1.0);
  } else {
    newColor *= vec4(0.0, 0.0, 1.0, 1.0);
  }
  newColor.xyz = rawColor.xyz * newColor.xyz;
  newColor.xyz = rawColor.xyz * (1 - newColor.w) + newColor.xyz * (newColor.w);
  FragColor = vec4(rawColor.xyz, 1.0) * letThrough +
    vec4(newColor.xyz, 1.0) * (1 - letThrough);
  //caution: FragColor.w should always be 1.0, otherwise we need to disable gl_blend.
}