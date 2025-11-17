import { Button, Drawer, type DrawerProps, Flex, Select, Stack } from '@mantine/core';
import { type ProfileResponse, useUpdateProfile } from '@/api/profile';
import { useForm } from '@mantine/form';
import { profileSchema, type ProfileSchema } from '@/api/profile/profile.schema.ts';
import { yupResolver } from 'mantine-form-yup-resolver';
import { showNotification } from '@mantine/notifications';
import { GOOGLE_MAP_LANGUAGES } from '@/constants/googleMap.ts';
import { InterestsField } from '@/components/Personalization/InterestsField.tsx';
import { TravelStyleField } from '@/components/Personalization/TravelStyleField.tsx';

export const PersonalizationDrawer = ({ opened, onClose, data }: DrawerProps & { data: ProfileResponse }) => {
    const { mutate: updateProfile } = useUpdateProfile();
    const form = useForm<ProfileSchema>({
        validateInputOnChange: true,
        validate: yupResolver(profileSchema),
        initialValues: data,
    });

    const onSubmit = (values: ProfileSchema) => {
        updateProfile(values, {
            onSuccess: () => {
                showNotification({
                    title: 'Успех',
                    message: 'Ваши интересы обновлены!',
                    color: 'green',
                    autoClose: 3000,
                });
                onClose()
            },
            onError: (err) => {
                console.error('Ошибка при сохранении интересов', err);
                onClose()
            },
        });
    }

    return (
        <Drawer title="Изменение персонализации" opened={opened} onClose={onClose}>
            <form onSubmit={form.onSubmit(onSubmit)}>
                <Stack>
                    <Select
                        label="Язык озвучки"
                        {...form.getInputProps('language')}
                        searchable
                        allowDeselect={false}
                        data={GOOGLE_MAP_LANGUAGES}
                    />
                    <InterestsField label="Интересы" {...form.getInputProps('interests')} />
                    <TravelStyleField label="Тип путешественника" {...form.getInputProps('travelStyle')} />

                    <Flex mt="md" justify="space-between" gap="md">
                        <Button color="dark" variant="light" onClick={onClose}>Отменить</Button>
                        <Button type="submit">Сохранить</Button>
                    </Flex>
                </Stack>
            </form>
        </Drawer>
    );
};