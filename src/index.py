class State:
    def __init__(self, **kwargs):
        self._state = kwargs

    def set(self, key, value):
        self._state[key] = value

    def get(self, key):
        return self._state.get(key)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)


class Component:
    def __init__(self, render_func, state=None):
        self.render_func = render_func
        self.state = state

    def render(self):
        return self.render_func(self.state)


class App:
    def __init__(self):
        self.components = []
        self.routes = {}

    def add_component(self, component):
        self.components.append(component)

    def define_route(self, path, handler):
        self.routes[path] = handler

    def render(self):
        components_html = "\n".join([component.render() for component in self.components])
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dynamic App</title>
            <style>
                .light {{ background-color: white; color: black; }}
                .dark {{ background-color: black; color: white; }}
            </style>
        </head>
        <body>
            {components_html}
        </body>
        </html>
        """


def create_event(name, handler_path):
    return f"""
    <script>
        function {name}() {{
            fetch('{handler_path}', {{ method: 'POST' }})
                .then(() => window.location.reload());
        }}
    </script>
    """


# 상태 및 앱 정의
state = State(light_or_dark="light")
app = App()

# 메인 컴포넌트 정의
def main_component(state):
    toggle_script = create_event("toggleDarkMode", "/toggle-dark-mode")
    return f"""
    {toggle_script}
    <div class="main {state['light_or_dark']}">
        <h1>Hello</h1>
        <button onclick="toggleDarkMode()">Toggle Dark Mode</button>
    </div>
    """


# 카운터 상태 정의
counter_state = State(val=1)

def counter_component(state):
    counter = create_event("counterEvent", "/counter")
    reset = create_event("resetEvent", "/reset")
    return f"""
    {counter}
    {reset}
    <div>
        <h1>Counter: {state['val']}</h1>
        <button onclick="counterEvent()">Increment</button>
        <button onclick="resetEvent()">Reset</button>
    </div>
    """

# 컴포넌트 추가
main = Component(main_component, state)
counter = Component(counter_component, counter_state)

app.add_component(main)
app.add_component(counter)

# Flask와 연결
from flask import Flask

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return app.render()

# 다크모드 토글 처리
@flask_app.route("/toggle-dark-mode", methods=["POST"])
def toggle_dark_mode():
    state["light_or_dark"] = "dark" if state["light_or_dark"] == "light" else "light"
    return "", 204

# 카운터 증가 처리
@flask_app.route("/counter", methods=["POST"])
def counter():
    counter_state["val"] += 1  # 카운터 값을 증가시킴
    return "", 204  # 상태 업데이트 후 빈 응답 반환

# 카운터 리셋 처리
@flask_app.route("/reset", methods=["POST"])
def reset():
    counter_state["val"] = 0  # 카운터 값을 0으로 리셋
    return "", 204  # 상태 업데이트 후 빈 응답 반환

if __name__ == "__main__":
    flask_app.run(debug=True)
