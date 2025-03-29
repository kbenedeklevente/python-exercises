import json
import os
import time
import argparse
import shlex

class TaskTracker:
    def __init__(self):
        self.file_name = "./task_tracker.json"

        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w') as file:
                self.tasks = {}
                json.dump(self.tasks, file)
        else:
            with open(self.file_name, 'r') as file:
                self.tasks = {int(k): v for k, v in json.load(file).items()}

    def __save_tasks(self):
        with open(self.file_name, 'w') as file:
            json.dump(self.tasks, file)

    def add(self, task_description):
        next_id = int(max(self.tasks.keys(), default=0)) + 1
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        task = {
            "description": task_description,
            "status": "todo",
            "createdAt": current_time,
            "updatedAt": current_time
        }
        self.tasks[next_id] = task
        self.__save_tasks()
        print(f"Task added succesfully (ID: {next_id})")
    
    def update(self, id, task_description=None, status=None):
        if id in self.tasks:
            task = self.tasks[id]
            task['description'] = task_description if task_description else task['description']
            task['status'] = status if status else task['status']
            task['updatedAt'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.__save_tasks()
        else:
            print("Id not found. Please try again.")

    def delete(self, id):
        if id in self.tasks:
            del self.tasks[id]
            self.__save_tasks()
        else:
            print("Id not found. Please try again.")

    def list_tasks(self, status=None):
        if status:
            print({k: v for k, v in self.tasks.items() if v['status'] == status})
        else:
            print(self.tasks)

def __main__():
    task_tracker = TaskTracker()

    parser = argparse.ArgumentParser(description="CLI for tracking tasks.")
    subparsers = parser.add_subparsers(dest='command')

    add_parser = subparsers.add_parser('add', help="Add a new task")
    add_parser.add_argument('description', type=str, help="Description of task")

    update_parser = subparsers.add_parser('update', help="Update the description of a specific task")
    update_parser.add_argument('id', type=int, help="Id of task")
    update_parser.add_argument('description', type=str, help="New description of task")

    delete_parser = subparsers.add_parser('delete', help="Delete a specific task")
    delete_parser.add_argument('id', type=int, help="Id of task")

    mark_progress_parser = subparsers.add_parser('mark-in-progress', help="Set the status of a task to \"in progress\"")
    mark_progress_parser.add_argument('id', type=int, help="Id of task")

    mark_done_parser = subparsers.add_parser('mark-done', help="Set the status of a task to \"in progress\"")
    mark_done_parser.add_argument('id', type=int, help="Id of task")

    list_parser = subparsers.add_parser('list', help="List all tasks. Use [done, todo, in-progress] arguments for a list filtered by status")
    list_parser.add_argument('filter', type=str, choices=['done', 'todo', 'in-progress'], help="Filter tasks by status", nargs='?')

    while True:
        command = input("task-cli ").strip()

        if command.lower() == "quit":
            print("Exiting")
            break

        try:
            args = parser.parse_args(shlex.split(command))
            if args.command == 'add':
                task_tracker.add(args.description)
            elif args.command == 'update':
                task_tracker.update(args.id, description=args.description)
            elif args.command == 'delete':
                task_tracker.delete(args.id)
            elif args.command == 'mark-in-progress':
                task_tracker.update(args.id, status='in-progess')
            elif args.command == 'mark-done':
                task_tracker.update(args.id, status='done')
            elif args.command == 'list':
                task_tracker.list_tasks(args.filter)
            else:
                pass

        except SystemExit:
            continue


if __name__ == "__main__":
    __main__() 