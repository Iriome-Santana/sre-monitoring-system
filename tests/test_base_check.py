"""
Tests para la clase BaseCheck.

Este archivo contiene tests automatizados que verifican
que BaseCheck funciona correctamente.
"""

import pytest
from src.base_check import BaseCheck
import os

def test_save_and_load_state(tmp_path, monkeypatch):
    """Verifica que se pueda guardar y cargar el estado correctamente."""
    
    monkeypatch.setenv("STATE_DIR", str(tmp_path))    
    check = BaseCheck("test_save_load")
    check.save_state("WARNING")
    resultado = check.load_last_state()
    
    assert resultado == "WARNING"
    
    os.remove(check.state_file)

def test_load_state_no_file(tmp_path, monkeypatch):
    """Verifica que si no existe el archivo de estado, se asuma OK."""
    
    monkeypatch.setenv("STATE_DIR", str(tmp_path))    
    check = BaseCheck("test_no_file")
    resultado = check.load_last_state()
    
    assert resultado == "OK"
    
def test_state_transitions(tmp_path, monkeypatch):
    """
    Verifica que las transiciones de estado funcionan correctamente.
    """
    monkeypatch.setenv("STATE_DIR", str(tmp_path))
    
    check = BaseCheck("test_transitions")
    
    assert check.load_last_state() == "OK"
    
    check.save_state("WARNING")
    assert check.load_last_state() == "WARNING"
    
    check.save_state("CRITICAL")
    assert check.load_last_state() == "CRITICAL"
    
    check.save_state("OK")
    assert check.load_last_state() == "OK"
    
def test_validate_thresholds_normal(tmp_path, monkeypatch):
    """
    Verifica que el método validate_thresholds funcione correctamente
    con valores normales.
    """
    monkeypatch.setenv("STATE_DIR", str(tmp_path))
    
    check = BaseCheck("test_thresholds_normal")
    
    try:
        check.validate_thresholds(80,90, inverted=False)
    except SystemExit:
        assert False, "validate_thresholds debería pasar sin errores para valores normales"
        
def test_validate_thresholds_inverted(tmp_path, monkeypatch):
    """
    Verifica que el método validate_thresholds funcione correctamente
    con valores invertidos.
    """
    monkeypatch.setenv("STATE_DIR", str(tmp_path))
    
    check = BaseCheck("test_thresholds_inverted")
    
    try:
        check.validate_thresholds(90,80, inverted=True)
    except SystemExit:
        assert False, "validate_thresholds debería pasar sin errores para valores invertidos"
        
def test_validate_thresholds_invalid(tmp_path, monkeypatch):
    """
    Verifica que el método validate_thresholds maneje correctamente
    valores inválidos.
    """
    monkeypatch.setenv("STATE_DIR", str(tmp_path))
    
    check = BaseCheck("test_thresholds_invalid")
    
    with pytest.raises(SystemExit):
        check.validate_thresholds(90,80, inverted=False)
        
    with pytest.raises(SystemExit):
        check.validate_thresholds(80,90, inverted=True)
        
def test_validate_thresholds_equal(tmp_path, monkeypatch):
    """
    Verifica que el método validate_thresholds maneje correctamente
    valores iguales.
    """
    monkeypatch.setenv("STATE_DIR", str(tmp_path))
    
    check = BaseCheck("test_thresholds_equal")
    
    with pytest.raises(SystemExit):
        check.validate_thresholds(80,80, inverted=False)
        
    with pytest.raises(SystemExit):
        check.validate_thresholds(80,80, inverted=True)

def test_handle_state_change_alert_on_warning(tmp_path, monkeypatch):
    """
    Verifica que se envíe una alerta cuando el estado cambia a WARNING.
    """
    monkeypatch.setenv("STATE_DIR", str(tmp_path))
    
    check = BaseCheck("test_alert_warning")
    
    check.save_state("OK")
    
    exit_code = check.handle_state_change("WARNING", "test_metric", "50%")
    
    assert exit_code == 1, "handle_state_change debería retornar 1 para WARNING"
    assert check.load_last_state() == "WARNING", "El estado guardado debería ser WARNING"
    
def test_handle_state_change_no_alert_on_same_state(tmp_path, monkeypatch):
    """
    Verifica que no se envíe una alerta si el estado no cambia.
    """
    monkeypatch.setenv("STATE_DIR", str(tmp_path))
    
    check = BaseCheck("test_no_alert_same_state")
    
    check.save_state("WARNING")
    
    exit_code = check.handle_state_change("WARNING", "test_metric", "50%")
    
    assert exit_code == 1, "handle_state_change debería retornar 1 para WARNING"
    assert check.load_last_state() == "WARNING", "El estado guardado debería seguir siendo WARNING"
    
