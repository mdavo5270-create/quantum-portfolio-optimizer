"""Tests pour le script hello_world (Phase 0)."""

from src.hello_world import main


def test_main_runs_without_error(capsys):
    """Le script doit s'exécuter sans lever d'exception et afficher le message attendu."""
    main()
    captured = capsys.readouterr()
    assert "environnement OK" in captured.out
    assert "PAS un conseil financier" in captured.out
