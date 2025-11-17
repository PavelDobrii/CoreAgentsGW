import { useState } from 'react';
import { useNavigate } from 'react-router';
import { registerFormSchema, type RegisterFormSchema } from './registerForm.schema.ts';
import { useAuthContext } from '@/contexts';
import { yupResolver } from 'mantine-form-yup-resolver';
import { useForm } from '@mantine/form';
import { Button, PasswordInput, Stack, TextInput } from '@mantine/core';

export const RegisterForm = () => {
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { onRegister } = useAuthContext();

    const form = useForm<RegisterFormSchema>({
        validateInputOnChange: true,
        validate: yupResolver(registerFormSchema),
        initialValues: {
            email: '',
            password: '',
            re_password: '',
        },
    });

    const onSubmit = async ({ email, password}: RegisterFormSchema) => {
        setIsLoading(true);
        const response = await onRegister({ email, password });

        if (response) {
            navigate('/onboarding');
        }

        setIsLoading(false);
    };

    return (
        <form onSubmit={form.onSubmit(onSubmit)}>
            <Stack>
                <TextInput
                    placeholder="Электронная почта"
                    disabled={isLoading}
                    {...form.getInputProps('email')}
                />

                <PasswordInput
                    placeholder="Пароль"
                    disabled={isLoading}
                    {...form.getInputProps('password')}
                />

                <PasswordInput
                    placeholder="Подтверждение пароля"
                    disabled={isLoading}
                    {...form.getInputProps('re_password')}
                />

                <Button type="submit" size="md" fullWidth disabled={isLoading} loading={isLoading}>
                    Регистрация
                </Button>
            </Stack>
        </form>
    );
};
