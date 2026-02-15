import subprocess
import sys

def run_command(command):
    try:
        print(f"Выполняю: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nПрервано пользователем.")
        sys.exit(1)

def main():
    clear_cmd = ["sudo", "rm", "-rf", "work/", "out/"]
    
    build_cmd = ["sudo", "mkarchiso", "-v", "-w", "work/", "-o", "out/", "sosaltix-profile/"]

    run_command(clear_cmd)
    run_command(build_cmd)
    
    print("\nГотово! Сборка завершена успешно.")

if __name__ == "__main__":
    main()
