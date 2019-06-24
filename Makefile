REGISTRY = registry.dev
HASH_SUM = `./docker/check_enviroment_changes.sh`
SE_ENV_CONTAINER = $(REGISTRY)/sele:$(HASH_SUM)


# !!!!! parsing arguments !!!!!!!
ifeq (se-pull,$(firstword $(MAKECMDGOALS)))
  SEPULL_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
endif

ifeq (se-test,$(firstword $(MAKECMDGOALS)))
  SETEST_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
endif


se-build:
	@echo "==================================================================="
	@echo ">>>> [BUILD docker images]"
	@if [ -z "$$(docker images -q $(SE_ENV_CONTAINER))" ]; then \
		sh ./docker/build.sh; \
	else \
		echo ">>>> Found local container '$(SE_ENV_CONTAINER)'"; \
	fi;
	@echo ">>>> Done."


se-pull:
	@# [example]: make se-pull sele
	@# [example]: make se-pull sele:d6eb12c2
	@echo "==================================================================="
	@echo ">>>> [PULL docker images]"
	@docker login $(REGISTRY)
	@echo ">>>> Please wait, i'm pulling..."

	@if [ ! -z "$(SEPULL_ARGS)" ]; then \
		docker pull $(REGISTRY)/$(SEPULL_ARGS); \
		echo ">>>> Done."; \
	else \
		if [ "$$(docker pull $(SE_ENV_CONTAINER) 2> /dev/null)" != "" ]; then \
			echo ">>>> Download $(SE_ENV_CONTAINER)"; \
			echo ">>>> Done."; \
		else \
			echo "==================================================================="; \
			echo ">>>> [Not found container $(SE_ENV_CONTAINER)], use command 'make se-build'"; \
		fi; \
	fi;


se-push:
	@echo "==================================================================="
	@echo ">>>> [PUSH docker images]"
	@docker login $(REGISTRY)
	docker push $(SE_ENV_CONTAINER)
	@echo ">>>> Pushed $(SE_ENV_CONTAINER) in: https://gitlab.dev/container_registry"
	@echo ">>>> Done."


se-test:
	@# [example]: make se-test -- tests/ (...)
	@echo "==================================================================="
	@echo ">>>> [RUN tests in docker]"
	@xhost +SI:localuser:root
	@echo "" > .pytest_cache/v/cache/lastfailed &2>/dev/null
	@#@if [ -z "$$(docker images -q $(SE_ENV_CONTAINER))" ]; then \
		#echo ">>>> Don't found local container '$(SE_ENV_CONTAINER)', try upload from registry..."; \
		#$(MAKE) -s se-pull; \
	#fi;
	@if [ -z "$$(docker images -q $(SE_ENV_CONTAINER))" ]; then \
		echo ">>>> Don't found in registry container '$(SE_ENV_CONTAINER)', build new container..."; \
		$(MAKE) -s se-build; \
	fi;
	@$(MAKE) -s se-remove-old-images
	@docker run --net=host -v "$(PWD)":/work -it $(SE_ENV_CONTAINER) $(SETEST_ARGS)


se-version:
	@# actual container version
	@echo $(SE_ENV_CONTAINER)


se-remove-old-images:
	@# save last 5 images, and remove all another
	@python docker/remove_old_images.py $(REGISTRY)/sele
