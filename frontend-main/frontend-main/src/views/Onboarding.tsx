import { useState } from 'react';
import { useNavigate } from 'react-router';
import {
    Button,
    Divider,
    Flex,
    Group,
    Space,
    Text,
    Radio, Title, InputError, Select, InputDescription,
} from '@mantine/core';
import { ChevronsLeft, ChevronsRight } from 'lucide-react';
import { ScreenView } from '@/components/ScreenView';
import { Gender, useUpdateProfile } from '@/api/profile';
import { showNotification } from '@mantine/notifications';
import { useDocumentTitle } from '@mantine/hooks';
import { useForm } from '@mantine/form';
import { onboardingSchema, type OnboardingSchema } from '@/api/profile/profile.schema.ts';
import { yupResolver } from 'mantine-form-yup-resolver';
import { GOOGLE_MAP_LANGUAGES } from '@/constants/googleMap.ts';
import { InterestsField, TravelStyleField } from '@/components/Personalization';

type StepKey = 1 | 2 | 3 | 4;

const LAST_STEP = 4

const ONBOARDING_MAP: Record<StepKey, { label: string; fieldName: string; description?: string; }> = {
    1: { fieldName: 'gender', label: 'Укажи свой пол:' },
    2: { fieldName: 'travelStyle', label: 'Какой ты путешественник?' },
    3: { fieldName: 'interests', label: 'Что тебе интересно?' },
    4: {
        fieldName: 'language',
        label: 'На каком языке хочешь слушать истории',
        description: 'Можно изменить позже в профиле'
    },
};

export const Onboarding = () => {
    useDocumentTitle('Персонализация — Gowee');
    const navigate = useNavigate();

    const { mutate: updateProfile } = useUpdateProfile();

    const [currentStep, setCurrentStep] = useState(1)

    const form = useForm<OnboardingSchema>({
        validateInputOnChange: true,
        validate: yupResolver(onboardingSchema),
        initialValues: {
            language: 'ru-RU'
        },
    });

    const activeStep = ONBOARDING_MAP[currentStep as StepKey];
    const activeStepError = form.errors[activeStep?.fieldName];

    const onClickPrev = () => {
        const prevStep = currentStep > 1 ? currentStep - 1 : currentStep;

        setCurrentStep(prevStep)
    }

    const onClickNext = () => {
        const { hasError } = form.validateField(activeStep?.fieldName)
        if (hasError) return

        const nextStep = currentStep < LAST_STEP ? currentStep + 1 : currentStep;

        setCurrentStep(nextStep)
    }

    const onSubmit = () => {
        const { hasErrors } = form.validate()
        if (hasErrors) {
            return;
        }

        updateProfile(form.values, {
            onSuccess: () => {
                showNotification({
                    title: 'Успех',
                    message: 'Ваши интересы сохранены! Создайте свой первый маршрут :)',
                    color: 'green',
                    autoClose: 3000,
                });

                navigate('/trip/create');
            },
            onError: (err) => {
                console.error('Ошибка при сохранении интересов', err);
                navigate('/trip/create');
            },
        });
    };

    return (
        <ScreenView footerOptions={{
            onRender: () => (
                <OnboardingFooter
                    onClickPrev={onClickPrev}
                    onClickNext={onClickNext}
                    onSubmit={onSubmit}
                    currentStep={currentStep}
                />
            )
        }}>
            <Flex direction="column" align="center" mb="xl" gap={4}>
                <Title order={1}>Персонализация</Title>
                <Text>Позвольте нам узнать вас лучше</Text>
            </Flex>

            <Divider my="xl" label={`${currentStep}/${LAST_STEP}`} labelPosition="left" />
            <Text size="sm" fw="700" mb={8}>{activeStep?.label}</Text>
            {activeStep?.description && !activeStepError && (
                <InputDescription mb="md">{activeStep?.description}</InputDescription>
            )}
            {activeStepError && <InputError mb="md">{activeStepError}</InputError>}

            <form>
                {currentStep === 1 && (
                    <Radio.Group {...form.getInputProps('gender')} error={null}>
                        <Group mt="xs">
                            <Radio value={Gender.Female} label="Девушка" />
                            <Radio value={Gender.Male} label="Парень" />
                        </Group>
                    </Radio.Group>
                )}
                {currentStep === 2 && <TravelStyleField {...form.getInputProps('travelStyle')} error={null} />}
                {currentStep === 3 && <InterestsField {...form.getInputProps('interests')} error={null} />}
                {currentStep === 4 && (
                    <Select
                        {...form.getInputProps('language')}
                        searchable
                        allowDeselect={false}
                        data={GOOGLE_MAP_LANGUAGES}
                        error={null}
                    />
                )}
            </form>
        </ScreenView>
    );
};

const OnboardingFooter = ({ onClickPrev, onClickNext, currentStep, onSubmit }: {
    currentStep: number;
    onClickPrev: () => void;
    onClickNext: () => void;
    onSubmit: () => void;
}) => {
    const isLastStep = currentStep === LAST_STEP;

    return (
        <Group justify="space-between" align="center">
            {currentStep !== 1 ? (
                <Button
                    size="sm"
                    variant="light"
                    color="dark"
                    leftSection={<ChevronsLeft size={20} />}
                    onClick={onClickPrev}
                >Назад</Button>
            ) : (
                <Space />
            )}

            {isLastStep ? (
                <Button onClick={onSubmit} size="sm">Сохранить</Button>
            ) : (
                <Button
                    size="sm"
                    rightSection={<ChevronsRight size={20} />}
                    onClick={onClickNext}
                >
                    Далее
                </Button>
            )}
        </Group>
    );
};