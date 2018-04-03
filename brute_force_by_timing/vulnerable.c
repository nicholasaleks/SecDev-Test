#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <time.h>
#include <string.h>

/* macros */
#define MAX_STR 255
#define die(x) { \
  errno = x; \
  perror(0x00); \
  return errno; \
};

#define USER_NAME   "james"
#define USER_SECRET "bond"

/* types */
typedef unsigned char uchar;
typedef unsigned int uint;
typedef struct Credentials credentials;
struct Credentials {
  const uchar *name;
  const uchar *secret;
};

/* forward prototypes */
uchar strcmp_slow(const int len, const uchar *a, const uchar *b);
uchar authenticate(const credentials *const input);

int main(int argc, char **argv)
{
  credentials input;
  if (argc > 3) die (E2BIG);
  if (argc < 3) die (EINVAL);
  input.name   = argv[1];
  input.secret = argv[2];
  return authenticate(&input);
}

uchar authenticate(const credentials *const input)
{
  static uint name_len   = strlen(USER_NAME),
              secret_len = strlen(USER_SECRET);
  uchar fail;

  fail = strcmp_slow(name_len,   input->name,   USER_NAME);
  if (fail)
    return 0x03;

  fail = strcmp_slow(secret_len, input->secret, USER_SECRET);
  if (fail)
    return 0x06;

  return 0x00;
}


/**
 * Returns 0x00 on success and 0xFF on failure.
 *
 * Success is defined as string equality, i.e. all chars are the same and the
 * terminal NUL on both strings is present.
 */
uchar strcmp_slow(const int len, const uchar *const a, const uchar *const b)
{
  static const struct timespec char_delay = { 0, 0x1000000LL };

  register int i;
  register uchar x;

  for (i=0; i < len; ++i) {

    /* slow down each cmp to make the attack easier */
    nanosleep(&char_delay, NULL);

    /* XOR is nonzero for all byte pairs except (0x00, 0x00) */
    x = a[i] ^ b[i];

    /* failure: inequality */
    if (x)
      return 0xFF;
  }
  /* failure: non-terminal nul in either string */
  if ((a[i] | b[i]) != 0x00)
    return 0xFF;

  /* success */
  return 0x00;
}
