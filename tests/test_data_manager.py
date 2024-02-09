import os
import pytest
import numbers

import risibot.data_manager as dm

@pytest.mark.asyncio
async def test_data_manager_ninja_data_loading():
    # Removing ninja data if any
    if os.path.isdir(dm.DATA_FOLDER_PATH):
        if os.path.isfile(dm.NINJA_DATA_PATH):
            os.remove(dm.NINJA_DATA_PATH)

    # Checking that retrieving functions return 
    # their default values
    assert dm.get_divine_price() == -1.0
    assert dm.get_poe_ninja_data('Test') is None
    
    # Checking data manager retrieves data correctly
    assert await dm.fetch_poe_ninja()

    # Checking corresponding data file has been created
    assert os.path.isdir(dm.DATA_FOLDER_PATH)
    assert os.path.isfile(dm.NINJA_DATA_PATH)

    # Checking data manager uses the cache
    assert not await dm.fetch_poe_ninja()

    # Checking that retrieving functions retrieve
    # non-default values once data is loaded
    assert dm.get_divine_price() != -1.0
    assert dm.get_poe_ninja_data('chaos')

    # Checking that data items are properly formatted
    for (name, item) in dm.POE_NINJA_DATA.items():
        assert isinstance(name, str)
        assert isinstance(item, dict)
        assert 'price' in item and isinstance(item['price'], numbers.Number)
        assert 'true_name' in item and isinstance(item['true_name'], str)
        assert 'is_equipment' in item and isinstance(item['is_equipment'], bool)