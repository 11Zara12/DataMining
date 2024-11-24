import subprocess

# 定义执行函数
def execute_script(script_name):
    try:
        # 使用 subprocess.run 执行脚本
        result = subprocess.run(['python', script_name], capture_output=True, text=True)

        # 输出执行结果
        if result.returncode == 0:
            print(f"Execution of {script_name} was successful.")
            print("OutputsForE:\n", result.stdout)
        else:
            print(f"Execution of {script_name} failed.")
            print("Error:\n", result.stderr)
    except Exception as e:
        print(f"An error occurred while trying to run {script_name}: {e}")


# 执行三个脚本
if __name__ == "__main__":
    scripts = ["./WithExternalLib/FuzzywuzzyOne.py", "./WithExternalLib/PylevenshteinOne.py", "./WithExternalLib/RapidfuzzOne.py"]

    for script in scripts:
        execute_script(script)
