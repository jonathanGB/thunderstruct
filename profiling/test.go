package main

import "C"

import "fmt"
import "time"

//export Foo
func Foo() {
	c := make(chan int)

	for i := 0; i < 10; i++ {
		go func(elem int) {
			time.Sleep(time.Duration(elem) *time.Second)
			c <- elem
		}(i)
	}

	for i := 0; i < 10; i++ {
		fmt.Println(<-c)

	}

	fmt.Println("DONE")
}

//export Print
func Print() {
	fmt.Println("Hello World")
}

func main() {}
