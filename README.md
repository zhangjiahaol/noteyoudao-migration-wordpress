# noteyoudao-migration-wordpress

# 因为有道笔记更新新版本之后有很多BUG与诸多使用上不爽的地方

# 本项目将有道笔记上的所有.note类型笔记全部迁移到wordpress中

# 准备环境： 
```
1、CentOS Linux release 7
2、yum install -y epel-release && yum install -y jq && yum install -y python36
3、在wordpress安装Application Passwords插件,并且替换wordpress_batch_import.sh脚本中的username、password变量token值
```

# 脚本执行步骤

## 1、执行获取有道笔记上的所有笔记，格式为docx
```
python getYoudaoAllNotes.py account*** password*** ./notes docx 
```

## 2、转换所有docx文件为html
```
find ./ -name "*.docx" -print |while read line
do
    file_name="${line##*/}"
    directory="${line%/*}"
    if [ -f "$line" ];then
	    echo -e "\033[32m ################# $line ################# \033[0m" 
		python3 docxToHtml.py "${line}"
    elif [ -d "$line" ];then
	    echo " "
        #echo "$line skip is dir..."
    else
        echo "############################ error ################################"
        echo "$line"
    fi
done
```

## 3、执行导入到wordpress
### 会将文件夹层级关系转换为WP分类层级，html通过WP API导入到文章
### 将wordpress_batch_import.sh脚本文件放到需要导入的html根目录顶层下，wordpress会根据脚本的所在目录下导入文章与分类
```
cp -a ./wordpress_batch_import.sh ./notes/
cd ./notes/
chmod +x wordpress_batch_import.sh
./wordpress_batch_import.sh
```


