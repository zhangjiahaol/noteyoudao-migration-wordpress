#!/bin/bash

###script_name: wordpress_batch_import.sh
###author: jiahaozhang
###此脚本基于REST API批量操作wordpress
###本脚本依赖yum install jq
###可以使用unoconv工具批量将各种格式文档转换成html或者python模块
###此脚本会自动导入当前文件夹包含子文件夹下的所有.html文件，并且会自动根据目录路径递归创建分类
###需要安装Application Passwords插件，并且替换username、password变量token值
###将wordpress_batch_import.sh文件放到需要导入的当前目录下
###配置脚本中的参数wordpress_batch_import.sh
###执行此脚本开始批量导入./wordpress_batch_import.sh


domain='http://jiahao.love'
username='jiahao'
password='2QuBOcDVkvCRdNJ83RqtmJXr'



CategoriesID="-1"
#创建分类
DirPathCreateToCategorize()
{
### ./root/test/test1
# 递归创建分类
echo "$(echo "$1" | sed 's#/#\n#g')" > /tmp/DirPathCreateToCategorize.txt
while read cate
do
    ### root
    categorize_name="$cate"
    if [ "$categorize_name" == "." ]||[ "$categorize_name" == "" ];then
        continue
    fi
    if [ "$CategoriesID" != "-1" ];then
        #创建子分类
        result=$(curl ${domain}/wp-json/wp/v2/categories -L -X POST --user "${username}:${password}" -d "description=${categorize_name}&name=${categorize_name}&slug=''&parent=${CategoriesID}" |jq '.id')
        #如果子分类等于空说明已经创建过此分类，则获取此分类的已有的ID
        if [ "$result" == "" ]||[ "$result" == "null" ];then
            result=$(curl ${domain}/wp-json/wp/v2/categories -L -X POST --user "${username}:${password}" -d "description=${categorize_name}&name=${categorize_name}&slug=''&parent=${CategoriesID}" |jq '.data.term_id')
            echo "Already created..."
        fi
        CategoriesID=$result
    else
        #创建分类
        result=$(curl ${domain}/wp-json/wp/v2/categories -L -X POST --user "${username}:${password}" -d "description=${categorize_name}&name=${categorize_name}&slug=''" |jq '.id')
        #如果分类等于空说明已经创建过此分类，则获取此分类的已有的ID
        if [ "$result" == "" ]||[ "$result" == "null" ];then
            result=$(curl ${domain}/wp-json/wp/v2/categories -L -X POST --user "${username}:${password}" -d "description=${categorize_name}&name=${categorize_name}&slug=''" |jq '.data.term_id')
            echo "Already created categories..."
        fi
        CategoriesID=$result
    fi
    echo "DirPathCreateToCategorize: CategoriesID=$CategoriesID"
done < /tmp/DirPathCreateToCategorize.txt
}

#导入文章
ImportDocument()
{
    FilePath="$1"
    file_name=$(echo "$FilePath" |awk -F '/' '{print $NF}' |sed 's:.note.docx.html::g')
    CategoriesID="$2"
    echo "###### ImportDocument: FilePath: $1   CategoriesID: $2 ######"
    \cp -fa "$FilePath" /tmp/temp.html
    if [ "$?" == "0" ];then
        sed -i 's#\\#\\\\#g' /tmp/temp.html
        sed -i ':a;N;$!ba;s/\n/\\n/g' /tmp/temp.html
        sed -i 's#\t#\\t#g'  /tmp/temp.html
        sed -i 's#"#\\"#g' /tmp/temp.html
        sed -i "1i{\"title\": \"${file_name}\",\"content\": \"" /tmp/temp.html
        sed -i '$a","status": "publish","categories":['${CategoriesID}']}' /tmp/temp.html
        curl -i -o /dev/null -s -w %{http_code} ${domain}/wp-json/wp/v2/posts -L -X POST \
            -H "Content-Type: application/json"  \
            --user "${username}:${password}" \
            -d @/tmp/temp.html
    else
        echo "############################ 1: ${1} , 2: ${2} ################################"
    fi
}


#开始批量处理
find ./ -name "*.html" -print > /tmp/batch.txt
while read line
do
    CategoriesID="-1"
    file_name=$(basename "$line")
    directory=$(dirname "$line")
    if [ -f "$line" ];then
        echo " "
        echo -e "\033[32m ################# $line ################# \033[0m" 
        # create categorize
        DirPathCreateToCategorize "$directory"
        # Import Document
        ImportDocument "$line" "$CategoriesID"
    elif [ -d "$line" ];then
        echo " "
        #echo "$line skip is dir..."
    else
        echo "############################ error ################################"
        echo "$line"
    fi
    sleep 1
done < /tmp/batch.txt



