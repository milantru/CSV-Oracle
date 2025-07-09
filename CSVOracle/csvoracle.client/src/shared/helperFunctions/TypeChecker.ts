/** Checks whether provided value is a number. */
export function isNumber(value?: string | number): boolean {
	return (!!value && !isNaN(Number(value.toString())));
}
