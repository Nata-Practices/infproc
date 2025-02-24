import http.client
import os
import threading
from http.server import CGIHTTPRequestHandler, HTTPServer
from tkinter import messagebox, simpledialog

import requests

from tasks.base_graph import BaseGraphApp

# Увеличение лимита заголовков
http.client._MAXHEADERS = 1000


class HTTPApp(BaseGraphApp):
    def __init__(self, root):
        super().__init__(root, "Протокол HTTP", "4")
        self.server_thread = None
        self.httpd = None
        self.predefined_url = ""  # Переменная для заранее указанного ресурса
        self.saves_dir = "saves"
        os.makedirs(self.saves_dir, exist_ok=True)
        self.add_button("Получить опции сервера", self.get_server_options)
        self.add_button("GET запрос", lambda: self.fetch_resource(method='GET'))
        self.add_button("POST запрос", lambda: self.fetch_resource(method='POST'))
        self.add_button("POST запрос на получение переменных", lambda: self.fetch_resource(method='CUSTOM'))
        self.add_button("HEAD запрос", lambda: self.fetch_resource(method='HEAD'))

        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.run_cgi_server()

    def get_server_options(self):
        try:
            # Получение опций для всего сервера
            server_response = requests.options("http://localhost:8000")
            server_options = "\n".join([f"{key}: {value}" for key, value in server_response.headers.items()])
            messagebox.showinfo("Опции сервера", f"Опции самого сервера:\n{server_options}")

            # Получение опций для конкретного ресурса, например, index.html
            resource_url = "http://localhost:8000/index.html"
            resource_response = requests.options(resource_url)
            resource_options = "\n".join([f"{key}: {value}" for key, value in resource_response.headers.items()])
            messagebox.showinfo("Опции ресурса", f"Опции ресурса (index.html):\n{resource_options}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def fetch_resource(self, method):
        if method == 'CUSTOM':
            url = "http://localhost:8000/cgi-bin/environment.py"
            data = {"key": "value"}
        else:
            url = self.ask_for_url_or_use_predefined()
            if not url:
                return
            data = None

        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, data=data)
            elif method == 'CUSTOM':
                response = requests.post(url, data=data)
            elif method == 'HEAD':
                response = requests.head(url)
            else:
                messagebox.showerror("Ошибка", "Неподдерживаемый метод")
                return

            headers_file = os.path.join(self.saves_dir, f"response_headers_{method}.txt")
            content_file = os.path.join(self.saves_dir, f"response_content_{method}.html")

            with open(headers_file, 'w', encoding='utf-8') as f:
                for key, value in response.headers.items():
                    f.write(f"{key}: {value}\n")

            if response.text:
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)

            messagebox.showinfo("Успех", f"Заголовки сохранены в {headers_file}\nСодержимое сохранено в {content_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def ask_for_url_or_use_predefined(self):
        if self.predefined_url:
            return self.predefined_url
        return simpledialog.askstring("Введите URL", "Введите адрес сервера (например, http://localhost:8000)")

    def run_cgi_server(self):
        cgi_script_content = """\
import os

def generate_html():
    print("Content-Type: text/html")
    print("")  # Пустая строка после заголовка обязательна!
    print("<html><body><h1>Environment Variables</h1><table border=1>")
    for key, value in os.environ.items():
        print(f"<tr><td>{{key}}</td><td>{{value}}</td></tr>")
    print("</table></body></html>")

generate_html()
        """

        try:
            cgi_dir = "cgi-bin"
            os.makedirs(cgi_dir, exist_ok=True)
            cgi_file = os.path.join(cgi_dir, "environment.py")
            with open(cgi_file, 'w', encoding='utf-8') as f:
                f.write(cgi_script_content)

            self.httpd = HTTPServer(('localhost', 8000), CGIHTTPRequestHandler)

            def start_server():
                self.httpd.serve_forever()

            self.server_thread = threading.Thread(target=start_server)
            self.server_thread.daemon = True
            self.server_thread.start()

            messagebox.showinfo("Сервер CGI", "Сервер запущен на http://localhost:8000")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def stop_cgi_server(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None

    def on_close(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.stop_cgi_server()
            self.root.destroy()