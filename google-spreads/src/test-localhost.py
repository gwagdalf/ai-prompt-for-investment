from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def callback():
    code = request.args.get('code')
    return f"인증 코드: {code}" # 여기서 코드를 복사하면 됩니다.

if __name__ == '__main__':
    app.run(port=8080)