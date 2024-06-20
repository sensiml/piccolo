
THIS_DIR          := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))
OUT               := $(abspath $(THIS_DIR))

ifndef SENSIML_SDK_PATH
SENSIML_SDK_PATH = ../../
endif
ifndef SENSIML_COMMON_PATH
SENSIML_COMMON_PATH = ../../../server/codegen/templates/common
endif

IFLAGS := -I../include -I. -I$(SENSIML_SDK_PATH)include -I$(SENSIML_COMMON_PATH)
CFLAGS += -std=c99 -fPIC -fno-builtin -Werror $(IFLAGS)

fgsrc_path :=
fgsrc := \
	tree_ensemble.c

fgsrc_full := $(addprefix $(fgsrc_path), $(fgsrc))
fgobjs_full := $(patsubst %.c, %.o, $(fgsrc_full))
fgobjs_local := $(patsubst %.c, %.o, $(fgsrc))

SRC := $(fgsrc_full)
OBJS := $(patsubst %.c, %.o, $(fgobjs_local))
COBJS := $(patsubst %.c, %.o, $(SRC))

LIB = $(OUT)/libclassifiers.so



$(OUT)/%.o:$(SRC)
	@echo "what am i doing"
	@echo $(ANSI_RED)"[cPP]"$(ANSI_OFF) $@ $^
	@echo $(COBJS)
	$(AT)$(CC) $(CFLAGS) -c -o $@ $^



$(LIB): $(COBJS)
	@echo "making lib"
	@echo $(LDFLAGS)
	$(AT)$(AR) rcs $@ $(OBJS)
	$(AT)$(CC) -shared -Wl,-o libclassifiers.so *.o


clean:
	@echo $(ANSI_RED)"[CLEAN]"$(ANSI_OFF) $@
	rm -f $(OBJS) $(LIB)
	rm -f *.so

main: $(LIB)

install:
	cp $(LIB) $(INSTALL_PATH)


all: lib

.PHONY:	lib all clean installofiles

