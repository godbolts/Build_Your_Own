// https://blog.init-io.net/post/2018/07-01-go-unix-shell/

package main

import (
	"bufio"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"os/user"
	"strings"
)

func main() {
	reader := bufio.NewReader(os.Stdin)
	for {
		user, _ := user.Current()
		host, _ := os.Hostname()
		dir, _ := os.Getwd()
		fmt.Print("[" + host + "] " + "(" + user.Username + ") " + dir + "> ")
		input, err := reader.ReadString('\n')
		if err != nil {
			fmt.Fprintln(os.Stderr, err)

		}
		if err = execInput(input); err != nil {
			fmt.Fprintln(os.Stderr, err)
		}
	}
}

func execInput(input string) error {
	input = strings.TrimSpace(input)
	args := strings.Split(input, " ")

	switch args[0] {
	case "cd":
		if len(args) < 2 {
			return errors.New("path required")
		}
		return os.Chdir(args[1])
	case "exit":
		os.Exit(0)
	}

	cmd := exec.Command(args[0], args[1:]...)

	cmd.Stderr = os.Stderr
	cmd.Stdout = os.Stdout

	return cmd.Run()
}
