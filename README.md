# TASKIFY 

```Taskify``` is a minimalistic telegram bot that allows you to create a schedule: task lists, tasks, as well as shared lists for several users.

## Getting Started

## `Launch`

To launch, clone the project and enter the following commands in the root of the repository

```bash
docker build -t taskify .
docker run --rm -v $(pwd)/data:/app/data taskify
```

P.S. The project is configured to run in Docker. For most Linux operating systems, the following commands will suffice for its installation

```bash
curl -fsSL https://get.docker.com -o install-docker.sh
sudo sh install-docker.sh
```

## `Bot`

To get started, enter the command `@thtaskbot` in the Telegram user
```
/start
```
The output will be:
```
Hello, User! I'm Taskify bot.
Here you can create your own task lists and tasks.

Here is your personal ID: ***********
```

This is how you register in the bot and get your ID for further collaboration
## Interface
Every time you start working, just enter the command

```
/menu
```

## `Task-листы и задачи`

Task lists have two types - simple and note. The former removes the task from the list when you complete it, the latter does not. Note lists are good for regular processes - like products that you want to buy.

The `task lists` button takes you to a menu with viewing and creating lists. Creating lists and
tasks has a single form: your message will take the form of a list/task, where in `<>` you will need to
enter the necessary data. There will be hints for the corresponding fields. Do not worry about doing something wrong: the bot will not accept an incorrectly entered task. To create, simply
click on the creation message: it will highlight itself, offering to do this as soon as you
enter the task/list completely.

## `Collaborators`

The lists have the ability to add collaborators: to do this, click on the corresponding button in the list and enter the ID of the person you are collaborating with. This person will not be able to change the tasks, but will be able to view them and mark them as completed.

## `О задачах`
The `All tasks` command will display all tasks - from your lists and those lists where you participate in the role of a collaborator. Tasks can be marked as completed both in it and in task lists. When
clicking on a task, a menu for editing it and the ability to delete it will open - these things can only be done by the owner of the list.
