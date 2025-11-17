import { GeoPicker } from '@/components/GeoPicker';
import { useHeader } from '@/hooks';
import { useForm } from '@mantine/form';
import { yupResolver } from 'mantine-form-yup-resolver';
import {
    Accordion,
    Autocomplete,
    Button,
    Loader,
    MultiSelect, type OptionsFilter,
    Select,
    Stack,
    Text,
    TextInput,
} from '@mantine/core';
import { tripSchema, type TripSchema, useCreateTrip } from '@/api/trips';
import { showNotification } from '@mantine/notifications';
import { useNavigate } from 'react-router';
import { DateInput } from '@mantine/dates';
import { useDebouncedValue, useDocumentTitle } from '@mantine/hooks';
import { DURATION_OPTIONS, MOOD_OPTIONS, TIME_OF_DAY_OPTIONS } from '@/constants/options.ts';
import { type Place, usePlaces } from '@/api/places';
import { type ChangeEvent, useEffect, useState } from 'react';
import { Plus, Settings2 } from 'lucide-react';
import { InterestsField } from '@/components/Personalization';
import { useProfile } from '@/api/profile';

const noFilter: OptionsFilter = ({ options }) => options;

export const TripCreate = () => {
    useDocumentTitle('Новое путешествие — Gowee');
    useHeader({ title: 'Новое путешествие' });

    const navigate = useNavigate();
    const { mutate: createTrip, isPending } = useCreateTrip();
    const { data: profileData } = useProfile();

    const form = useForm<TripSchema>({
        validateInputOnChange: true,
        validate: yupResolver(tripSchema),
        initialValues: {
            title: '',
            description: '',
            localityId: '',
            start: null,
            end: null,
            routeOptions: {
                dateAt: '',
                duration: 'four',
                interests: [],
            },
        },
    });

    const [search, setSearch] = useState('');
    const [selectedLocality, setSelectedLocality] = useState<Place | null>(null);
    const [debouncedSearch] = useDebouncedValue(form.values.localityId ? '' : search, 300);
    const { data: localityData, isFetching } = usePlaces({
        query: debouncedSearch.trim(),
        type: 'locality',
    });

    const handleInput = (e: ChangeEvent<HTMLInputElement>) => {
        const value = e.currentTarget.value;

        setSearch(value);
        setSelectedLocality(null);
        form.setFieldValue('localityId', null);
    };

    const handleSelect = (placeId: string) => {
        const foundPlace = localityData?.find((item) => item.id === placeId);
        if (!foundPlace) return;

        setSelectedLocality(foundPlace);
        setSearch(foundPlace.address);
        form.setFieldValue('localityId', foundPlace.id);
    };

    const onSubmit = (values: TripSchema) => {
        createTrip(values,
            {
                onSuccess: (data) => {
                    showNotification({
                        title: 'Успех',
                        message: 'Путешествие записано!',
                        color: 'green',
                        autoClose: 3000,
                    });

                    navigate(`/trip/create/${data.id}`, { replace: true });
                },
                onError: (err) => {
                    console.error('Ошибка при создании путешествия', err);
                },
            },
        );
    };

    useEffect(() => {
        const hasFormInterests = form.values.routeOptions?.interests.length;
        if (!profileData?.interests || hasFormInterests) {
            return;
        }
        form.setFieldValue('routeOptions.interests', profileData.interests);
    }, [profileData]);

    return (
        <form onSubmit={form.onSubmit(onSubmit)}>
            <Stack>
                <TextInput label="Название маршрута" {...form.getInputProps('title')} />

                <Autocomplete
                    value={search}
                    label="Город"
                    withAsterisk
                    onInput={handleInput}
                    error={form.errors.localityId}
                    data={localityData?.map(({ id, name }) => ({ value: id, label: name }))}
                    onOptionSubmit={handleSelect}
                    renderOption={({ option }) => {
                        const renderItem = localityData?.find(({ id }) => id === option.value);
                        if (!renderItem) return;
                        return (
                            <Stack gap={0}>
                                {renderItem.name}
                                <Text size="xs" c="dimmed" truncate="end">{renderItem.address}</Text>
                            </Stack>
                        );
                    }}
                    filter={noFilter}
                    rightSection={isFetching && <Loader size="xs" />}
                    w="100%"
                />

                <Accordion chevronSize={14}>
                    <Accordion.Item value="settings">
                        <Accordion.Control icon={<Settings2 />}>
                            <Text size="sm">Дополнительные настройки</Text>
                        </Accordion.Control>
                        <Accordion.Panel>
                            <GeoPicker
                                label="Старт маршрута"
                                disabled={!form.values.localityId}
                                description={!form.values.localityId ? 'Для выбора точки необходимо указать город' : ''}
                                defaultPlace={selectedLocality}
                                {...form.getInputProps('start')}
                            />

                            <GeoPicker
                                label="Конец маршрута"
                                disabled={!form.values.localityId}
                                description={!form.values.localityId ? 'Для выбора точки необходимо указать город' : ''}
                                defaultPlace={selectedLocality}
                                {...form.getInputProps('end')}
                            />

                            <DateInput
                                valueFormat="DD MMM YYYY"
                                label="Дата поездки"
                                {...form.getInputProps('routeOptions.dateAt')}
                            />

                            <Select
                                label="Время начала прогулки"
                                data={TIME_OF_DAY_OPTIONS}
                                allowDeselect={false}
                                {...form.getInputProps('routeOptions.timeOfDay')}
                            />
                        </Accordion.Panel>
                    </Accordion.Item>
                </Accordion>

                <Select
                    label="Время прогулки"
                    data={DURATION_OPTIONS}
                    allowDeselect={false}
                    {...form.getInputProps('routeOptions.duration')}
                />

                <MultiSelect
                    label="Твое настроение"
                    description="Выбери до 3 вариантов"
                    nothingFoundMessage="Ничего не найдено..."
                    searchable
                    maxValues={3}
                    data={MOOD_OPTIONS}
                    {...form.getInputProps('routeOptions.mood')}
                />

                <InterestsField label="Что тебе интересно?" {...form.getInputProps('routeOptions.interests')} />

                <Button type="submit" size="md" mt="md" fullWidth loading={isPending} leftSection={<Plus />}>
                    Создать путешествие
                </Button>
            </Stack>
        </form>
    );
};
