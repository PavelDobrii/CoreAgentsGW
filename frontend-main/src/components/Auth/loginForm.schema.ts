import { type InferType, object, string } from 'yup';

export const loginFormSchema = object({
    email: string().email().required().max(50).label('Email'),
    password: string().min(8).required().label('Password'),
});

export type LoginFormSchema = InferType<typeof loginFormSchema>
