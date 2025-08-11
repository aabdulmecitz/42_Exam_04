#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

int			picoshell(char **cmds[]);

#define RST "\033[0m"
#define BOLD "\033[1m"
#define GRN "\033[32m"
#define RED "\033[31m"
#define CYN "\033[36m"

static void	print_result(const char *name, int ok)
{
	if (ok)
		printf("  %s[PASS]%s %s\n", GRN, RST, name);
	else
		printf("  %s[FAIL]%s %s\n", RED, RST, name);
}

static int	test_ls_grep(void)
{
	char		*cmd1[] = {"sh", "-c", "printf 'a\nB\nccc\n'", NULL};
	char		*cmd2[] = {"grep", "c", NULL};
	char		**pipe1[] = {cmd1, cmd2, NULL};
	const char	*outfile = ".pico_out";
	pid_t		pid;
	FILE		*f;
	int			fd;
	int			ret;
	int			status;
	FILE		*rf;
	char		buf[256];
	size_t		n;
	const char	*expect = "ccc\n";

	unlink(outfile);
	pid = fork();
	if (pid == -1)
		return (0);
	if (pid == 0)
	{
		f = fopen(outfile, "w");
		if (!f)
			_exit(1);
		fd = fileno(f);
		dup2(fd, STDOUT_FILENO);
		fclose(f);
		ret = picoshell(pipe1);
		_exit(ret);
	}
	waitpid(pid, &status, 0);
	rf = fopen(outfile, "r");
	if (!rf)
		return (0);
	n = fread(buf, 1, sizeof(buf), rf);
	fclose(rf);
	unlink(outfile);
	return (WIFEXITED(status) && WEXITSTATUS(status) == 0)
		&& (n == strlen(expect) && memcmp(buf, expect, n) == 0);
}

static int	test_three_stage(void)
{
	char		*c1[] = {"sh", "-c", "printf 'ab'", NULL};
	char		*c2[] = {"sed", "s/b/c/", NULL};
	char		*c3[] = {"tr", "a-z", "A-Z", NULL};
	char		**pp[] = {c1, c2, c3, NULL};
	const char	*outfile = ".pico_out2";
	pid_t		pid;
	FILE		*f;
	int			fd;
	int			ret;
	int			status;
	FILE		*rf;
	char		buf[256];
	size_t		n;
	const char	*expect = "AC";

	unlink(outfile);
	pid = fork();
	if (pid == -1)
		return (0);
	if (pid == 0)
	{
		f = fopen(outfile, "w");
		if (!f)
			_exit(1);
		fd = fileno(f);
		dup2(fd, STDOUT_FILENO);
		fclose(f);
		ret = picoshell(pp);
		_exit(ret);
	}
	waitpid(pid, &status, 0);
	rf = fopen(outfile, "r");
	if (!rf)
		return (0);
	n = fread(buf, 1, sizeof(buf), rf);
	fclose(rf);
	unlink(outfile);
	return (WIFEXITED(status) && WEXITSTATUS(status) == 0)
		&& (n == strlen(expect) && memcmp(buf, expect, n) == 0);
}

int	main(void)
{
	int	passed = 0, total;
	int	ok;

	passed = 0, total = 0;
	printf("\n%s[PicoShell Tests]%s %s(2 cases)%s\n", BOLD, RST, CYN, RST);
	total++;
	ok = test_ls_grep();
	passed += ok;
	print_result("2-stage: printf | grep c => ccc", ok);
	total++;
	ok = test_three_stage();
	passed += ok;
	print_result("3-stage: printf | sed | tr => AC", ok);
	if (passed == total)
		printf("%sAll tests passed%s (%d/%d)\n", GRN, RST, passed, total);
	else
		printf("%sSome tests failed%s (%d/%d)\n", RED, RST, passed, total);
	return (passed == total ? 0 : 1);
}
