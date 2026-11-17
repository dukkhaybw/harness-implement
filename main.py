from colorama import init, Fore, Style
from agent import agent_loop
from hooks import trigger_user_prompt_hooks

init(autoreset=True)


def main():
    print("输入问题，回车发送。输入 q 退出。")

    history = []

    while True:
        try:
            query = input(Fore.GREEN + ">> " + Style.RESET_ALL)

        except (EOFError, KeyboardInterrupt):
            break

        if query.strip().lower() in ["q", "quit", "exit"]:
            break

        query = trigger_user_prompt_hooks(query)

        # 将用户问题添加到历史记录中
        history.append({"role": "user", "content": query})

        agent_loop(history)

        final_response = history[-1]

        if final_response.get("role") == "assistant":
            print(Fore.RED + final_response.get("content") + Style.RESET_ALL)


if __name__ == "__main__":
    main()
