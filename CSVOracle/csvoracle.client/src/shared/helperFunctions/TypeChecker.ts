export function isNumber(value?: string | number): boolean {
	return (!!value && !isNaN(Number(value.toString())));
}
