import { useState } from 'react';
import { useNavigate, Link } from 'react-router';
import { useAuthContext } from '@/contexts';
import { TextInput, PasswordInput, Button, Stack, Group } from '@mantine/core';
import { useForm } from '@mantine/form';
import { loginFormSchema, type LoginFormSchema } from './loginForm.schema';
import { yupResolver } from 'mantine-form-yup-resolver';

export const LoginForm = () => {
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { onLogin } = useAuthContext();

    const form = useForm<LoginFormSchema>({
        validateInputOnChange: true,
        validate: yupResolver(loginFormSchema),
        initialValues: {
            email: '',
            password: '',
        },
    });

    const onSubmit = async (values: LoginFormSchema) => {
        setIsLoading(true);
        const response = await onLogin(values);

        if (response) {
            navigate('/trips');
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

                <Stack>
                    <PasswordInput
                        placeholder="Пароль"
                        disabled={isLoading}
                        {...form.getInputProps('password')}
                    />
                    <Group justify="end">
                        <Link to="/auth/recover">Забыли пароль?</Link>
                    </Group>
                </Stack>

                <Button type="submit" size="md" fullWidth disabled={isLoading} loading={isLoading}>
                    Вход
                </Button>
            </Stack>
        </form>
    );
};
