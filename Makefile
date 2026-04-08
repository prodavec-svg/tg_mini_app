.PHONY: dev backend frontend

dev:
	@trap 'kill 0' SIGINT; \
	$(MAKE) backend & \
	$(MAKE) frontend & \
	wait

backend:
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm start
