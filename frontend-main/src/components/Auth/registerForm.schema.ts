import { type InferType, object, string } from 'yup';

export const registerFormSchema = object({
    email: string().email().required().max(50).label('Email'),
    password: string().min(8).required().label('Password'),
    re_password: string().required().label('Repeat password')
        .test(
            'passwords-match',
            'The passwords entered do not match',
            function (value) {
                if (!value) return true;
                return value === this.parent.password;
            },
        ),
});

export type RegisterFormSchema = InferType<typeof registerFormSchema>