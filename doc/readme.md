#lambdaimage文档
##源码位置
blade12:~/lambdaimage/
##环境需求

- spark==1.3.0
- hadoop==1.0
- python==2.7
- Cython==0.22.1
- decorator==3.4.2
- ipython==3.1.0
- matplotlib==1.4.3
- mock==1.0.1
- networkx==1.9.1
- nose==1.3.7
- numpy==1.9.2
- pandas==0.16.1
- Pillow==2.8.2
- pyparsing==2.0.3
- python-dateutil==2.4.2
- pytz==2015.4
- PyWavelets==0.2.2
- scikit-image==0.11.3
- scipy==0.15.1
- six==1.9.0
- wheel==0.24.0

##环境配置:
###spark环境配置
主节点: blade12    
计算节点: blade13 blade16 blade17

###hadoop环境配置
主节点: blade12    
数据节点: blade13 blade16 blade17

###python环境配置

    PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/build:/home/wb/lambdaimage:$PATHONPATH
    LD_LIBRARY_PATH=/home/wb/opt/fftw/lib:$LD_LIBARAY_PATH
    C_INCLUDE_PATH=/home/wb/opt/fftw/include:$C_INCLUDE_PATH
    CPLUS_INCLUDE_PATH=/home/wb/opt/fftw/include:$CPLUS_INCLUDE_PATH

##项目结构
###主目录

-lambdaimage             主目录    
 | + doc                 文档    
 | + test                单元测试    
 | + script              可执行脚本    
 | + lambdaimage         核心代码    
 | -Makefile             C代码编译规则    
 | -requirements.txt     需求的python库    
 | -setup                安装规则    

###核心代码目录

-lambdaimage             核心代码目录
 | + fusion              融合    
 | + imgprocessing       二维反卷积    
 | + preprocess          预处理    
 | + rdds                相关数据结构    
 | + registration        对准    
 | + segmentation        分割    
 | + serial              串行程序   
 | + udf                 C语言相关文件    
 | + utils               通用依赖库和数据文件

##执行
所有的测试数据和最终结果都存放在目录/home/wb/data/中.    

    cd lambdaimage
    pip install -r requirements.txt
    python setup.py install

###local模式
(1)执行单元测试

    cd test
    sh run_tests.sh

(2)执行主程序    

    cd script
    python mehi_local.python2

###standalone模式
- 在每个计算节点安装相应的依赖库，如PIL库.(注意python版本,这里使用的2.7)
- 将Richardson Lucy编译好的库 fftw库 scp到计算节点，并将路径加入到LD_LIBRARY_PATH
- 配置计算节点的库函数装载路径    
  修改  /etc/ld.so.conf 增加/home/yourusername/lib    
  修改完成后执行命令:ldconfig
- 将 scp_lib 中的库函数 scp到计算节点（blade13 14 16 17)中的~/lib路径下。
- 将lambdaimage目录scp到各个计算节点,并且分别安装:    
  make clean    
  make    
  python setup.py install

执行之前检查输入文件是否存在,rdd默认collect到主节点之后输出,可以在exportAsTiff函数中传递参数collectToDriver控制.

    cd 到主节点的script目录
    start-all.sh  启动spark
    spark-submit mehi_standalone.py --master spark://blade12:7077  --driver-memory 10G --executor-memory 6G

##其他
- 源码和二维反卷积文档在office/wb/目录下.
- spark安装参考[这里](http://blog.csdn.net/hxpjava1/article/details/19177913)
- hadoop安装参考[这里](http://www.cnblogs.com/lanxuezaipiao/p/3525554.html)
- python多版本共存,pyenv安装参考[这里](http://seisman.info/python-pyenv.html)
