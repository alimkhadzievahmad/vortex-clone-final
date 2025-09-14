from app import app

# Vercel handler
def handler(request):
    """Handler для Vercel"""
    return app(request.environ, lambda *args: None)

# Для локального тестирования
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
