# timer
一个计时器程序



## 下载地址

[下载地址](https://1drv.ms/u/s!AuCYFvwp2KHMgo16dPul4tZzEe79hw?e=gQNwYv)



## CHANGELOG

[CHANGELOG](./CHANGELOG.MD)



## 制作
### 更新翻译
```text
pyside2-lupdate timer.pro 
```
然后利用qtlinguist程序编辑生成的ts文件来制作qm文件。


### 更新资源
```text
pyside2-rcc timer.qrc -o timer_rc.py
```

### 制作exe
```text
pyinstaller timer.spec
```

### 制作安装包
利用nsis刷nsi脚本