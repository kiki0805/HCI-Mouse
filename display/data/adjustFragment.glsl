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
    rawColor = rawColor * 100.0f / 255.0f + vec4(80.0f/255.0f, 80.0f/255.0f,80.0f/255.0f,0);
    if (letThrough == 1) {
        FragColor = rawColor;
        FragColor.w = 1.0f;
    } else {
        float temp = texture(texture0, TexCoord).x;
        float temp2 = texture(texture0, TexCoord).y;
        float temp3 = texture(texture0, TexCoord).z;
        float pct = (90.0 / 255.0) / (temp + temp2 + temp3);
        float fluc30 = 30.0f / 255.0f;
        // float fluc20 = 20.0f / 255.0f;
        // FragColor = vec4(temp + fluc30*(1.0f/0.3f)*( rawColor.x * 2 - 1), 
        //     temp + fluc30*(1.0f/0.3f)*(rawColor.y * 2 - 1), temp + fluc30*(1.0f/0.3f)*(rawColor.z * 2 - 1), 1.0);
        // FragColor = vec4(rawColor.x + fluc30*(1.0f/0.3f)*( temp * 2 - 1), 
        //     rawColor.y + fluc30*(1.0f/0.3f)*(temp * 2 - 1), rawColor.z + fluc30*(1.0f/0.3f)*(temp * 2 - 1), 1.0);
        // if((temp+temp2+temp3)<=180.0f/255.0f) {
        //     float tmp = (1.0f / 0.3f) * ( rawColor.x * 2 - 1); // [-1, 1]
        //     tmp = (tmp / 2.0) * (2.0 * pct) + (1.0 - pct);
        //     float r = temp * tmp;
        //     tmp = (1.0f / 0.3f) * ( rawColor.y * 2 - 1); // [-1, 1]
        //     tmp = (tmp / 2.0) * (2.0 * pct) + (1.0 - pct);
        //     float g = temp2 * tmp;
        //     tmp = (1.0f / 0.3f) * ( rawColor.z * 2 - 1); // [-1, 1]
        //     tmp = (tmp / 2.0) * (2.0 * pct) + (1.0 - pct);
        //     float b = temp3 * tmp;
        //     FragColor = vec4(r,g,b,1.0);
        // }
        // else
            FragColor = vec4(temp * rawColor.x * 2,temp * rawColor.y * 2,temp * rawColor.z * 2, 1.0);
            // FragColor = vec4(temp * rawColor.x * 2,temp2 * rawColor.y * 2,temp3 * rawColor.z * 2, 1.0);
        // FragColor = vec4(temp, temp, temp, 1.0);
    }
    //vec4(texture(texture0, TexCoord).xyz, texture(texture0, TexCoord).w) * (1 - letThrough);
    //caution: FragColor.w should always be newColor.w so the gl_blend will be correct
}
