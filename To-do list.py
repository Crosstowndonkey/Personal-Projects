import tkinter as tk #tkinter is a GUI Library
from tkinter import messagebox


class Task: #create a class for Task which includes if completed and the description
    def __init__(self, description):
        self.description = description
        self.completed = False

    def mark_as_completed(self):
        self.completed = True

    def __str__(self):
        return self.description + (" (Completed)" if self.completed else "")


class ToDoList:
    def __init__(self):
        self.tasks = []

    def add_task(self, description):
        task = Task(description)
        self.tasks.append(task)

    def complete_task(self, task_index):
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index].mark_as_completed()
        else:
            print("Invalid task number.")

    def delete_task(self, task_index):
        if 0 <= task_index < len(self.tasks):
            del self.tasks[task_index]
        else:
            print("Invalid task number.")

    def get_tasks(self):
        return [str(task) for task in self.tasks]
class ToDoApp:
    def __init__(self, root):
        self.todo_list = ToDoList()
        self.root = root
        self.root.title("To-Do List")

        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        self.task_entry = tk.Entry(self.frame, width=50)
        self.task_entry.pack(side=tk.LEFT, padx=10)
        self.add_button = tk.Button(self.frame, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT)

        self.listbox = tk.Listbox(root, width=80, height=20)
        self.listbox.pack(pady=10)

        self.complete_button = tk.Button(root, text="Complete Task", command=self.complete_task)
        self.complete_button.pack(side=tk.LEFT, padx=10)
        self.delete_button = tk.Button(root, text="Delete Task", command=self.delete_task)
        self.delete_button.pack(side=tk.RIGHT, padx=10)

    def add_task(self):
        task_description = self.task_entry.get()
        if task_description:
            self.todo_list.add_task(task_description)
            self.task_entry.delete(0, tk.END)
            self.update_listbox()
        else:
            messagebox.showwarning("Warning", "You must enter a task description.")

    def complete_task(self):
        selected_task_index = self.listbox.curselection()
        if selected_task_index:
            index = selected_task_index[0]
            self.todo_list.complete_task(index)
            self.update_listbox()
        else:
            messagebox.showwarning("Warning", "You must select a task to complete.")

    def delete_task(self):
        selected_task_index = self.listbox.curselection()
        if selected_task_index:
            index = selected_task_index[0]
            self.todo_list.delete_task(index)
            self.update_listbox()
        else:
            messagebox.showwarning("Warning", "You must select a task to delete.")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for task in self.todo_list.get_tasks():
            self.listbox.insert(tk.END, task)


if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
