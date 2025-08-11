#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

int			ft_popen(const char *file, char *const argv[], char type);

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

static int	read_all_fd(int fd, char **out, size_t *out_len)
{
	char	*buf;
	char	*nb;
	ssize_t	r;

	size_t cap, len;
	cap = 1024;
	len = 0;
	buf = malloc(cap);
	if (!buf)
		return (-1);
	for (;;)
	{
		if (len + 512 > cap)
		{
			cap *= 2;
			nb = realloc(buf, cap);
			if (!nb)
			{
				free(buf);
				return (-1);
			}
			buf = nb;
		}
		r = read(fd, buf + len, cap - len);
		if (r == 0)
			break ;
		if (r < 0)
		{
			free(buf);
			return (-1);
		}
		len += (size_t)r;
	}
	*out = buf;
	*out_len = len;
	return (0);
}

static int	test_read_echo(void)
{
	int		fd;
	char	*data;
	size_t	len;
	int		ok;

	fd = ft_popen("echo", (char *const[]){"echo", "hello", NULL}, 'r');
	if (fd < 0)
		return (0);
	data = NULL;
	len = 0;
	ok = 0;
	if (read_all_fd(fd, &data, &len) == 0)
		ok = (len == 6 && memcmp(data, "hello\n", 6) == 0);
	close(fd);
	free(data);
	return (ok);
}

static int	test_write_to_cat_via_file(void)
{
	const char	*outfile = ".tmp_out";
	int			fd;
	ssize_t		w;
	int			ok;
	int			f;
	char		*data;
	size_t		len;

	unlink(outfile);
	fd = ft_popen("sh", (char *const[]){"sh", "-c", "cat > .tmp_out", NULL},
			'w');
	if (fd < 0)
		return (0);
	const char *msg = "abcdef"; // 6 bytes, no newline
	w = write(fd, msg, 6);
	ok = (w == 6);
	close(fd);
	usleep(100000);
	f = open(outfile, O_RDONLY);
	if (f < 0)
		return (0);
	data = NULL;
	len = 0;
	if (read_all_fd(f, &data, &len) != 0)
	{
		close(f);
		return (0);
	}
	close(f);
	ok = ok && (len == 6 && memcmp(data, msg, 6) == 0);
	free(data);
	unlink(outfile);
	return (ok);
}

int	main(void)
{
	int	passed = 0, total;
	int	ok;

	passed = 0, total = 0;
	printf("\n%s[ft_popen Tests]%s %s(2 cases)%s\n", BOLD, RST, CYN, RST);
	ok = test_read_echo();
	passed += ok;
	total++;
	print_result("type 'r': echo => hello\\n", ok);
	ok = test_write_to_cat_via_file();
	passed += ok;
	total++;
	print_result("type 'w': cat > file", ok);
	if (passed == total)
		printf("%sAll tests passed%s (%d/%d)\n", GRN, RST, passed, total);
	else
		printf("%sSome tests failed%s (%d/%d)\n", RED, RST, passed, total);
	return (passed == total ? 0 : 1);
}
