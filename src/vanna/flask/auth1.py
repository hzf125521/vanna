from abc import ABC, abstractmethod
import flask
import requests
import json


class AuthInterface(ABC):
    @abstractmethod
    def get_user(self, flask_request) -> any:
        pass

    @abstractmethod
    def is_logged_in(self, user: any) -> bool:
        pass

    @abstractmethod
    def override_config_for_user(self, user: any, config: dict) -> dict:
        pass

    @abstractmethod
    def login_form(self) -> str:
        pass

    @abstractmethod
    def login_handler(self, flask_request) -> str:
        pass

    @abstractmethod
    def callback_handler(self, flask_request) -> str:
        pass

    @abstractmethod
    def logout_handler(self, flask_request) -> str:
        pass

class NoAuth(AuthInterface):
    def get_user(self, flask_request) -> any:
        return {}

    def is_logged_in(self, user: any) -> bool:
        return True

    def override_config_for_user(self, user: any, config: dict) -> dict:
        return config

    def login_form(self) -> str:
        return ''

    def login_handler(self, flask_request) -> str:
        return 'No login required'

    def callback_handler(self, flask_request) -> str:
        return 'No login required'

    def logout_handler(self, flask_request) -> str:
        return 'No login required'

class ApiAuth(AuthInterface):
    def __init__(self, auth_url="http://10.97.21.90:8233/eamservice/api/TokenAuth/Authenticate", secret_key=None):
        self.auth_url = auth_url
        self.secret_key = secret_key
        self.login_html = '''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>用户登录</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .login-container {
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    width: 350px;
                }
                h2 {
                    text-align: center;
                    color: #333;
                    margin-bottom: 20px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    color: #555;
                }
                input[type="text"], input[type="password"] {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    box-sizing: border-box;
                }
                button {
                    width: 100%;
                    padding: 10px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }
                button:hover {
                    background-color: #45a049;
                }
                .error-message {
                    color: red;
                    text-align: center;
                    margin-bottom: 15px;
                    display: none;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h2>用户登录</h2>
                <div id="error-message" class="error-message"></div>
                <form id="login-form" action="/auth/login" method="post">
                    <div class="form-group">
                        <label for="username">用户名</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">密码</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit">登录</button>
                </form>
            </div>
            
            <script>
                document.getElementById('login-form').addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    var username = document.getElementById('username').value;
                    var password = document.getElementById('password').value;
                    
                    fetch('/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            username: username,
                            password: password
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.href = '/';
                        } else {
                            document.getElementById('error-message').textContent = data.message || '登录失败，请检查用户名和密码。';
                            document.getElementById('error-message').style.display = 'block';
                        }
                    })
                    .catch(error => {
                        document.getElementById('error-message').textContent = '登录请求失败，请稍后再试。';
                        document.getElementById('error-message').style.display = 'block';
                    });
                });
            </script>
        </body>
        </html>
        '''

    def get_user(self, flask_request) -> any:
        # 从cookie或session获取用户信息
        if 'user_token' in flask.session:
            return {
                'token': flask.session['user_token'],
                'username': flask.session.get('username', ''),
                'user_id': flask.session.get('user_id', '')
            }
        return None

    def is_logged_in(self, user: any) -> bool:
        # 检查用户是否已登录
        return user is not None and 'token' in user and user['token']

    def override_config_for_user(self, user: any, config: dict) -> dict:
        # 在这里可以根据用户权限自定义配置
        return config

    def login_form(self) -> str:
        # 返回登录页面的HTML
        return self.login_html

    def login_handler(self, flask_request) -> str:
        try:
            # 从请求中获取用户名和密码
            if flask_request.is_json:
                data = flask_request.get_json()
                username = data.get('username')
                password = data.get('password')
            else:
                username = flask_request.form.get('username')
                password = flask_request.form.get('password')

            if not username or not password:
                return flask.jsonify({'success': False, 'message': '用户名和密码不能为空'})

            # 调用认证接口
            response = requests.post(
                self.auth_url,
                json={
                    "UserNameOrEmailAddress": username,
                    "Password": password,
                    "LoginMethod": 0  # 0表示密码登录
                }
            )
            
            # 处理认证结果
            if response.status_code == 200:
                resp_data = response.json()
                
                # 处理成功响应 - 根据实际API响应格式
                if resp_data.get('success') and resp_data.get('result'):
                    auth_data = resp_data.get('result')
                    
                    # 登录成功，将token存入session
                    flask.session['user_token'] = auth_data.get('accessToken')
                    flask.session['username'] = auth_data.get('userName', username)
                    flask.session['user_id'] = str(auth_data.get('userId', ''))
                    
                    return flask.jsonify({'success': True})
                # 处理有错误信息的响应
                elif resp_data.get('error'):
                    error_msg = f"登录失败：{resp_data['error']}"
                    return flask.jsonify({'success': False, 'message': error_msg})
                else:
                    return flask.jsonify({'success': False, 'message': '登录失败：无效的认证响应'})
            else:
                # 处理非200响应
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', f'登录失败，HTTP状态码：{response.status_code}')
                    return flask.jsonify({'success': False, 'message': error_msg})
                except:
                    return flask.jsonify({'success': False, 'message': f'登录失败，HTTP状态码：{response.status_code}'})
                
        except Exception as e:
            return flask.jsonify({'success': False, 'message': f'登录异常：{str(e)}'})

    def callback_handler(self, flask_request) -> str:
        # 本例中不需要callback，直接返回空内容
        return ''

    def logout_handler(self, flask_request) -> str:
        # 清除session中的用户信息
        flask.session.pop('user_token', None)
        flask.session.pop('username', None)
        flask.session.pop('user_id', None)
        
        # 重定向到首页
        return flask.redirect('/')
