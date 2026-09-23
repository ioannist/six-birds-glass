import pytest

from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.lenses.definability import definable_predicate_count, lens_image_size


@pytest.mark.parametrize("N", (4, 6, 8))
def test_definable_predicate_count_for_energy_image(N: int) -> None:
    image_size = N + 1

    assert definable_predicate_count(image_size) == 2 ** (N + 1)


@pytest.mark.parametrize("N", (6, 8))
def test_lens_image_size_for_energy_matches_realized_levels(N: int) -> None:
    assert lens_image_size(l_energy(config, N) for config in range(1 << N)) == N + 1


def test_definable_predicate_count_rejects_negative_image_size() -> None:
    with pytest.raises(ValueError):
        definable_predicate_count(-1)
