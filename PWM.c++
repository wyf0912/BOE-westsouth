
#include <wiringPi.h>
 
#define PWMPin 1    //定义PWM引脚
 
void setup();
 
int main (void)
{
    setup();
    intval = 0;
    intstep = 2;
    while(1)
    {
      if(val>1024)
      {
          step = -step;    
          val = 1024;
      }
      else if(val<0)
      {
          step = -step;
          val = 0;
      }
 
      pwmWrite(PWMPin,val);
      val+=step;
      delay(10);
  }
  return 0 ;
} 
/*初始化配置*/
void setup()
{
       wiringPiSetup ();         //wiringPi库初始化
       pinMode (PWMPin, PWM_OUTPUT);   //设置1为PWM输出    
}