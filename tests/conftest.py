# tests/conftest.py
import faulthandler, sys, os

# Activer le dump de stack en cas de blocage
faulthandler.enable()

# Dump toutes les 60s tant que pytest tourne → on voit immédiatement où ça bloque
faulthandler.dump_traceback_later(60, repeat=True)

# Option: rendre les features paresseuses en tests
os.environ.setdefault("MIA_FEATURES_EAGER_IMPORT", "0")
os.environ.setdefault("MIA_MQ_USE_REALTIME", "0")



