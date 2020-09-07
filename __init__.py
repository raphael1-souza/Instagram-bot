import inquirer
import sys
from src.controllers.follow import follow_target_followers


def show_menu():
    questions = [
        inquirer.List(
            "size",
            message="Olá, oque iremos fazer hoje ?",
            choices=[
                "Seguir Seguidores do alvo",
                "Remover seguidores não mútuos",
                "Exit"
            ],
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers["size"]


def leave():
    sys.exit(0)


def unfollow():
    print("Módulo em construção")


options = {
        "Seguir Seguidores do alvo": follow_target_followers,
        "Remover seguidores não mútuos": unfollow,
        "Exit": leave
    }


if __name__ == "__main__":
    option = show_menu()
    function = options[option]
    function()
