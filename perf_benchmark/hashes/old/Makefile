compile: hello.go for.go exercises-slices.go
	go build -i for.go
	go build -i hello.go
	go build -i exercises-slices.go

hello: compile
	./hello

for: compile
	./for

slices: compile
	./exercises-slices

compile_pow : pow.go
	go build -i pow.go

pow: compile_pow
	./pow 