# Comparisonator
##### For when you really need to rank things.

Do you know that feeling when there's this urge deep within you that tells you to compare things and make a 
ranking based on your choices?

In fact, this is precisely how this tool came to life. There was this **great** 
[album](https://en.wikipedia.org/wiki/Marching_in_Time) that came out recently and it was so good that I couldn't decide
which song I like the most. So, I created this tool, and now I know. And you can use it too!

## Usage
Clone the repository, then execute:
```shell
poetry install
```

Once you have installed the dependencies, you can run utility using the following command:
```shell
poetry run comparisonator
# or
poetry shell
> comparisonator
```

To create a new ranking session, use:
```shell
comparisonator session create
```
The command will ask you for session details. Alternatively, you can specify those details as parameters.
Use the `--help` flag to find out more about any given command.

As of now, you can only load a session from a file. Simply put all items in separate lines and save the file somewhere
close, then pass its path to the `session create` command. It's that simple.

Once a session has been created, you can start voting! To do so, run:
```shell
comparisonator vote interactive SESSION_ID
```

You can quit the voting session at any time by hitting `ctrl-c`. All previous votes will be saved and you can 
resume voting at any time using the same command.

You can view the results of a session at any time (even before all votes have been cast) by running:
```shell
comparisonator results SESSION_ID
```

## Features
Not much, currently. You can create a ranking session, interacively vote on items, and view the results. That's about 
it. I am, however, planning to add more features in the future.

## License
If, for some reason, you want to use or modify this tool, make sure to read the [LICENSE](/LICENSE) file first.

## Author
Yeah, that's me. I'm [Maciej Wilczyński](https://lupin.pl) and I do weird stuff with software.
