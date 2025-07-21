#!/bin/bash

# SSL证书配置脚本
# 用于在服务器上配置Let's Encrypt SSL证书

set -e

echo "开始配置SSL证书..."

# 检查证书文件是否存在
if [ ! -f "/etc/letsencrypt/live/xinguang.online/fullchain.pem" ]; then
    echo "错误: SSL证书文件不存在，请先运行certbot获取证书"
    exit 1
fi

if [ ! -f "/etc/letsencrypt/live/xinguang.online/privkey.pem" ]; then
    echo "错误: SSL私钥文件不存在，请先运行certbot获取证书"
    exit 1
fi

echo "SSL证书文件检查通过"

# 检查Nginx配置语法
echo "检查Nginx配置语法..."
docker-compose exec nginx nginx -t

if [ $? -eq 0 ]; then
    echo "Nginx配置语法检查通过"
else
    echo "错误: Nginx配置语法错误，请检查配置文件"
    exit 1
fi

# 重新加载Nginx配置
echo "重新加载Nginx配置..."
docker-compose exec nginx nginx -s reload

if [ $? -eq 0 ]; then
    echo "✅ SSL配置成功！"
    echo "现在可以通过以下地址访问:"
    echo "  - https://xinguang.online"
    echo "  - https://www.xinguang.online"
    echo "  - HTTP请求将自动重定向到HTTPS"
else
    echo "❌ Nginx重新加载失败"
    exit 1
fi

# 显示SSL证书信息
echo ""
echo "SSL证书信息:"
openssl x509 -in /etc/letsencrypt/live/xinguang.online/fullchain.pem -text -noout | grep -E "Subject:|Issuer:|Not Before:|Not After:"

echo ""
echo "🔒 SSL配置完成！网站现在支持HTTPS访问。"