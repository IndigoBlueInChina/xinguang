#!/usr/bin/env python3
"""生成Nginx基本认证用户文件的脚本"""

import os
import sys
import getpass
from pathlib import Path
from passlib.hash import apr_md5_crypt


def create_htpasswd_file(username: str, password: str, htpasswd_path: Path) -> bool:
    """创建.htpasswd文件
    
    Args:
        username: 用户名
        password: 密码
        htpasswd_path: .htpasswd文件路径
        
    Returns:
        bool: 是否创建成功
    """
    try:
        # 使用Apache MD5加密密码
        encrypted_password = apr_md5_crypt.hash(password)
        
        # 创建用户条目
        user_entry = f"{username}:{encrypted_password}\n"
        
        # 确保目录存在
        htpasswd_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查文件是否已存在
        if htpasswd_path.exists():
            # 读取现有内容
            with open(htpasswd_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 检查用户是否已存在
            user_exists = False
            for i, line in enumerate(lines):
                if line.startswith(f"{username}:"):
                    lines[i] = user_entry
                    user_exists = True
                    break
            
            # 如果用户不存在，添加新用户
            if not user_exists:
                lines.append(user_entry)
            
            # 写回文件
            with open(htpasswd_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        else:
            # 创建新文件
            with open(htpasswd_path, 'w', encoding='utf-8') as f:
                f.write(user_entry)
        
        print(f"✅ 用户 '{username}' 已成功添加到 {htpasswd_path}")
        return True
        
    except Exception as e:
        print(f"❌ 创建.htpasswd文件失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("🔐 易和书院 - Nginx用户认证文件生成器")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    htpasswd_path = project_root / "nginx" / ".htpasswd"
    
    print(f"📁 .htpasswd文件路径: {htpasswd_path}")
    print()
    
    try:
        # 获取用户名
        while True:
            username = input("👤 请输入用户名: ").strip()
            if username:
                break
            print("❌ 用户名不能为空，请重新输入")
        
        # 获取密码
        while True:
            password = getpass.getpass("🔑 请输入密码: ")
            if len(password) < 6:
                print("❌ 密码长度至少6位，请重新输入")
                continue
            
            confirm_password = getpass.getpass("🔑 请确认密码: ")
            if password == confirm_password:
                break
            print("❌ 两次输入的密码不一致，请重新输入")
        
        # 创建.htpasswd文件
        if create_htpasswd_file(username, password, htpasswd_path):
            print()
            print("🎉 用户认证文件创建成功！")
            print()
            print("📋 接下来的步骤:")
            print("1. 复制 .env.example 为 .env 并填写配置")
            print("2. 运行 docker-compose up -d 启动服务")
            print("3. 访问 http://localhost 并使用刚创建的用户名密码登录")
            print()
            print("💡 提示: 可以运行此脚本多次来添加更多用户")
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()