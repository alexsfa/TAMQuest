import pytest
from unittest.mock import MagicMock
from database.likert_scale_options import Likert_scale_options


class MockSupabaseResponse:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error


@pytest.fixture
def supabase_client():
    client = MagicMock()

    query = MagicMock()
    query.eq.return_value = query
    query.order.return_value = query

    client.table.return_value.select.return_value = query
    client.table.return_value.insert.return_value = query
    client.table.return_value.update.return_value = query

    return client


def test_get_options_by_likert_scale_id(supabase_client):
    expected_data = [
        {
            "id": "l_s_o_1",
            "value": 1,
            "label": "strongly disagree"
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    likert_scales_options = Likert_scale_options(supabase_client)

    result = likert_scales_options.get_options_by_likert_scale_id("l_s_123")

    assert result.data == expected_data


def test_create_likert_scale_options(supabase_client):
    inserted_data = [
        {
            "id": "l_s_o_123",
            "value": 1,
            "label": "Strongly Disagree",
        }
    ]

    supabase_client.table.return_value \
        .insert.return_value \
        .execute.return_value = MockSupabaseResponse(data=inserted_data)

    likert_scale_options = Likert_scale_options(supabase_client)

    result = likert_scale_options.create_likert_scale_options(
        likert_scale_options
    )

    assert result.data == inserted_data


def test_get_options_by_likert_scale_id_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.side_effect = Exception("DB down")

    likert_scales_options = Likert_scale_options(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        likert_scales_options.get_options_by_likert_scale_id("l_s_123")

    assert "Failed to retrieve the likert scale's options" in str(exc.value)


def test_create_likert_scale_options_fail(supabase_client):
    supabase_client.table.return_value \
        .insert.return_value \
        .execute.side_effect = Exception("DB down")

    likert_scale_options = Likert_scale_options(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        likert_scale_options.create_likert_scale_options([{"id": "l_s_o_1"}])

    assert "Failed to insert the likert scale's options" in str(exc.value)
