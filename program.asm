	.text
	.file	"<string>"
	.globl	main
	.p2align	4, 0x90
	.type	main,@function
main:
	.cfi_startproc
	pushq	%rsi
	.cfi_def_cfa_offset 16
	pushq	%rdi
	.cfi_def_cfa_offset 24
	subq	$56, %rsp
	.cfi_def_cfa_offset 80
	.cfi_offset %rdi, -24
	.cfi_offset %rsi, -16
	movabsq	$scanf_fmt, %rsi
	movabsq	$scanf, %rdi
	leaq	44(%rsp), %rdx
	movq	%rsi, %rcx
	callq	*%rdi
	leaq	40(%rsp), %rdx
	movq	%rsi, %rcx
	callq	*%rdi
	leaq	52(%rsp), %rdx
	movq	%rsi, %rcx
	callq	*%rdi
	movl	44(%rsp), %edx
	addl	40(%rsp), %edx
	movabsq	$printf_fmt, %rcx
	movabsq	$printf, %rdi
	callq	*%rdi
	movl	44(%rsp), %eax
	movl	%eax, %ecx
	imull	%ecx, %ecx
	movl	%ecx, 40(%rsp)
	leal	(%rcx,%rax), %edx
	movl	%edx, 48(%rsp)
	cmpl	%ecx, %eax
	jge	.LBB0_2
	movl	44(%rsp), %eax
	imull	%eax, %eax
	movl	%eax, 40(%rsp)
	jmp	.LBB0_3
.LBB0_2:
	movl	40(%rsp), %eax
	addl	44(%rsp), %eax
	movl	%eax, 48(%rsp)
.LBB0_3:
	movl	48(%rsp), %edx
	cvtsi2ss	%rdx, %xmm0
	divss	%xmm0, %xmm0
	movss	%xmm0, 52(%rsp)
	movabsq	$printf_fmt, %rsi
	movq	%rsi, %rcx
	callq	*%rdi
	movl	44(%rsp), %edx
	movq	%rsi, %rcx
	callq	*%rdi
	movl	40(%rsp), %edx
	movq	%rsi, %rcx
	callq	*%rdi
	addq	$56, %rsp
	popq	%rdi
	popq	%rsi
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc

	.type	scanf_fmt,@object
	.section	.rodata,"a",@progbits
	.globl	scanf_fmt
scanf_fmt:
	.asciz	"%d\000"
	.size	scanf_fmt, 4

	.type	printf_fmt,@object
	.globl	printf_fmt
printf_fmt:
	.asciz	"%d\n\000"
	.size	printf_fmt, 5

	.section	".note.GNU-stack","",@progbits
