import math

import click
from slugify import slugify

from src.entity.comparison import Comparison
from src.entity.session import Session
from src.error import AppError
from src.repository.comparison_engine import ComparisonEngineRepository
from src.repository.session import SessionRepository
from src.utils import Utils


@click.group()
def main():
    pass


@main.group()
def session():
    pass


@main.group()
def vote():
    pass


@session.command()
@click.option(
    "-n",
    "--name",
    "name",
    prompt=True,
    help="Name of the session",
    type=str,
)
@click.option(
    "-f",
    "--file",
    "filepath",
    prompt=True,
    help="Path to a file containing a list of items to compare",
    type=click.Path(),
)
@click.option(
    "-t",
    "--type",
    "check_type",
    prompt=True,
    help="Type of comparison. Use 'full' to compare each item with every other, or 'assuming' to assume some comparisons.",
    type=click.Choice(["full", "assuming"], case_sensitive=False),
)
@Utils.error_wrapped
def create(name: str, filepath: str, check_type: str):
    repo = SessionRepository()
    items = repo.load_items_from_file(filepath)
    slug = slugify(name)

    for s in repo.list_sessions():
        if s.id == slug:
            raise AppError(f"Session {slug} already exists")

    repo.save_session(
        Session(id=slug, name=name, comparison_type=check_type, items=items)
    )
    click.echo(f"Session {slug} created successfully!")


@session.command(name="list")
def list_sessions():
    repo = SessionRepository()
    click.echo("Sessions:")
    for s in repo.list_sessions():
        click.echo(f"  - {s.id} ({s.name})")


@session.command(name="delete")
@click.argument("session_id", type=str)
@Utils.error_wrapped
def delete(session_id: str):
    repo = SessionRepository()
    repo.delete_session(session_id)
    click.echo(f"Session {session_id} deleted successfully!")


@session.command(name="delete-all")
@Utils.error_wrapped
def delete_all():
    if click.confirm("Are you sure you want to delete all sessions?"):
        repo = SessionRepository()
        repo.delete_all_sessions()
        click.echo("All sessions deleted successfully!")
    else:
        click.echo("Aborted")


@vote.command(name="interactive")
@click.argument("session_id", type=str)
@Utils.error_wrapped
def interactive(session_id: str):
    session_repo = SessionRepository()
    session = session_repo.load_session(session_id)
    if not session:
        raise AppError(f"Session {session_id} does not exist")

    comparison_repo = ComparisonEngineRepository().get_comparison_repository(
        session
    )(session)
    while items := comparison_repo.get_next_comparison():
        comp_num = comparison_repo.get_finished_comparison_count() + 1
        pending_comparison_count = (
            comparison_repo.get_pending_comparison_count()
        )
        if pending_comparison_count is not None:
            all_num = (
                comparison_repo.get_finished_comparison_count()
                + pending_comparison_count
            )
            click.echo(
                click.style(
                    f"Comparison {comp_num} of {all_num}:",
                    fg="bright_white",
                    bold=True,
                )
            )
        else:
            click.echo(
                click.style(
                    f"Comparison {comp_num}:", fg="bright_white", bold=True
                )
            )

        for i, item in enumerate(items):
            click.echo(f"  - {i + 1}: {item.name}")

        while True:
            choice = click.prompt(
                "Enter the number of the item you think is better", type=int
            )
            if choice < 1 or choice > len(items):
                click.echo(f"Invalid choice {choice}", err=True)
                continue
            break

        comparison = Comparison(items=items, winner=(choice - 1))
        comparison_repo.save_comparison(comparison)
    click.echo(
        click.style(
            "All comparisons have been performed. Go ahead and check the results!",
            fg="bright_white",
            bold=True,
        )
    )


@main.command(name="results")
@click.argument("session_id", type=str)
@Utils.error_wrapped
def results(session_id: str):
    session_repo = SessionRepository()
    session = session_repo.load_session(session_id)
    if not session:
        raise AppError(f"Session {session_id} does not exist")

    comparison_repo = ComparisonEngineRepository().get_comparison_repository(
        session
    )(session)
    final_results = comparison_repo.get_next_comparison() is None
    click.echo(
        click.style(
            f"Results for session {session.name}:", fg="bright_white", bold=True
        )
    )
    results_list = comparison_repo.get_results()
    digits = int(math.log10(len(results_list)) + 1)
    previous_count = -1

    for i, item in enumerate(results_list):
        if item[1] is not None:
            if item[1] == previous_count:
                click.echo(f"   {''.rjust(digits+1)} {item[0]} ({item[1]})")
            else:
                click.echo(
                    f"   {str(i + 1).zfill(digits)}: {item[0]} ({item[1]})"
                )
            previous_count = item[1]
        else:
            click.echo(f"   {str(i + 1).zfill(digits)}: {item[0]}")

    click.echo(
        click.style(
            "Results are final."
            if final_results
            else "Results are not final. Some comparisons have not been completed yet.",
            fg="bright_white",
            bold=True,
        )
    )


if __name__ == "__main__":
    main()
