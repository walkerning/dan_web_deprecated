Dan Web
================

The website of Dan.


Requirements
----------------

libmysqlclient-dev


Run the Website
----------------

得到源代碼存放在${DAN_WEB}目錄中

### 安裝並配置mysql

#### mysql

```bash
$ sudo apt-get install mysql-server
```

在安裝過程中會要設置mysql的root帳戶的密碼

安裝完畢後, 使用``` mysql -u root -p ``` 然後輸入剛剛設置的密碼登陸mysql服務器

```mysql
CREATE DATABASE {DATABASE_NAME};
USE {DATABASE_NAME};
SOURCE  ${DAN_WEB}/database/schema_old.sql; // 創建完table
```

為了Python mysql client能夠正常work還需要裝以下包:

```bash
$ sudo apt-get install libmysqlclient-dev
```

新建一個用戶專門用於網站的數據庫的帳號

```mysql
CREATE USER '{MYSQL_USER}'@'localhost' IDENTIFIED BY '{MYSQL_USER_PASS}';
GRANT ALL PRIVILEGES ON {DATABASE_NAME}.* TO '{MYSQL_USER}'@'localhost' WITH GRANT OPTION;
```

### 配置依賴和環境

#### virtualenv

為了隔離依賴 ，可以使用``virtualenv``

```bash
sudo pip install virtualenv
virtualenv --system-site-packages venv
# 之後的操作均在這個venv下進行
```

#### anonconda

如果已經配置好了caffe, numpy應該已經有, 如果沒有，compression-tool依賴 `numpy`，可以安裝anaconda, 而且可以用mkl提速:

在[anoconda官網](https://www.continuum.io/downloads)上安裝anonconda，然後配置mkl

```bash
$ conda update conda
$ conda install mkl
```

#### caffe

按照[caffe官網](http://caffe.berkeleyvision.org/installation.html)的指導配置好caffe和pycaffe wrapper

#### compression-tool

安裝compression-tool

```bash
pip install git+https://github.com/angel-eye/compression-tool
```

運行 ```dan -h``` 查看幫助，並確認compression-tool已經裝好

#### 網站本身的依賴

```bash
cd ${DAN_WEB}
pip install -r requirement.txt
```

### 寫網站配置文件

源目錄下的``` app_conf.py.sample ``` 中的`SQLALCHEMY_DATABASE_URI`需要講其中的'{}'裡的值改成上面對應的值

```python
'mysql://{MYSQL_USER}:{MYSQL_USER_PASS}@localhost/{DATABASE_NAME}'
```

`DAN_WEB_PYCAFFE_PATH` 需改為當前機器上中pycaffe的路徑


### 創建用戶

 由於沒開放註冊功能，需由管理員手動創建

```make my-test-model```

然後運行

```python
new_user = User.create_user("{username}", "{userpassword}")
```



自动化部署
-----------------

自動化部署的脚本可以有，不過要以後才能來寫...
