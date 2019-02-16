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
    if (letThrough == 1) {
        FragColor = rawColor;
    } else {
        float temp = texture(texture0, TexCoord).x;
        // if (temp > 0.5) FragColor = vec4(1.0,1.0,1.0,1.0);
        // else FragColor = vec4(0.0,0.0,0.0,1.0);

        FragColor = vec4(temp + 0.3*(1 - rawColor.x * 2), temp + 0.3*(1 - rawColor.y * 2), temp + 0.3*(1 - rawColor.z * 2), 1.0);
        // FragColor = vec4(temp * rawColor.x * 2,temp * rawColor.y * 2,temp * rawColor.z * 2, 1.0);
        // FragColor = vec4(temp, temp, temp, 1.0);
    }
    //vec4(texture(texture0, TexCoord).xyz, texture(texture0, TexCoord).w) * (1 - letThrough);
    //caution: FragColor.w should always be newColor.w so the gl_blend will be correct
}
